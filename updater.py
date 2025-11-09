#!/usr/bin/env python3
"""
Packagemaker updater (PyQt5).

- Checks remote details.xml for version changes.
- Verifies whether a GitHub release with that tag contains a platform-specific binary.
  - If a binary asset is found, prompts the user to download & install it.
  - If the release exists but no binary for the platform is present, offers to install the source (BETA-DEV).
  - If no release tag exists: offers to install the source (BETA-DEV).
- Tries to show a native notification (Windows/Linux) but always presents an interactive Qt dialog for actions.
- Background threads perform checking and download/extract safely. Closing a notification never terminates the process.

Dependencies: PyQt5, requests
"""

import os
import sys
import time
import zipfile
import shutil
import requests
import subprocess
import platform
import xml.etree.ElementTree as ET
from typing import Tuple, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

# Optional native notification helpers (best-effort)
# Prefer Windows notification libraries (try win10toast_click, then winotify), and notify2 on Linux
_win10toaster = None
_winotify = None
try:
	from win10toast_click import ToastNotifier
	_win10toaster = ToastNotifier()
except Exception:
	_win10toaster = None
	try:
		from winotify import Notification as WinNotify, audio as WinAudio
		_winotify = WinNotify
	except Exception:
		_winotify = None
try:
	import notify2
	_notify2_inited = False
except Exception:
	notify2 = None
	_notify2_inited = False

REMOTE_XML = "https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/details.xml"
LOCAL_XML = "details.xml"
GITHUB_REPO = "JesusQuijada34/packagemaker"


class UpdateChecker(QtCore.QThread):
	update_found = QtCore.pyqtSignal(str, str)  # version, platform
	status = QtCore.pyqtSignal(str)
	error = QtCore.pyqtSignal(str)

	def __init__(self, interval: int = 180, parent=None):
		super().__init__(parent)
		self.interval = interval
		self._stopped = False

	def stop(self):
		self._stopped = True

	def run(self):
		# simple loop that checks remote version and emits event when different
		while not self._stopped:
			try:
				self.status.emit("Comprobando actualizaciones...")
				local = leer_version(LOCAL_XML)
				remote = leer_version_remota()
				if remote and remote != local:
					# pick first candidate platform and notify UI; UI will do a more thorough GitHub check
					plats = detect_platform_names()
					plat = plats[0] if plats else 'linux-x64'
					self.update_found.emit(remote, plat)
					return
				self.status.emit("Sin actualizaciones")
			except Exception as e:
				self.error.emit(str(e))

			waited = 0
			while waited < self.interval and not self._stopped:
				time.sleep(1)
				waited += 1


class DownloadWorker(QtCore.QThread):
	progress = QtCore.pyqtSignal(int)
	status = QtCore.pyqtSignal(str)
	finished_ok = QtCore.pyqtSignal()
	error = QtCore.pyqtSignal(str)

	def __init__(self, url: str, parent=None):
		super().__init__(parent)
		self.url = url
		self._stopped = False

	def run(self):
		destino = "update.zip"
		backup_dir = "backup_embestido"
		try:
			if not os.path.exists(backup_dir):
				os.makedirs(backup_dir, exist_ok=True)
			for f in os.listdir('.'):
				if f in (backup_dir, destino) or f.startswith('.'):
					continue
				if os.path.isfile(f):
					shutil.copy2(f, os.path.join(backup_dir, f))

			self.status.emit("Descargando...")
			resp = requests.get(self.url, stream=True, timeout=20)
			total = int(resp.headers.get('content-length', 0) or 0)
			downloaded = 0
			chunk = 8192
			with open(destino, 'wb') as fh:
				for data in resp.iter_content(chunk_size=chunk):
					if self._stopped:
						return
					if not data:
						continue
					fh.write(data)
					downloaded += len(data)
					if total:
						pct = int(downloaded * 100 / total)
						self.progress.emit(pct)

			self.status.emit('Extrayendo...')
			with zipfile.ZipFile(destino, 'r') as z:
				z.extractall('.')
			try:
				os.remove(destino)
			except Exception:
				pass

			# try to launch new binary if present
			if not sys.argv[0].endswith('.py'):
				executable = 'packagemaker.exe' if os.name == 'nt' else './packagemaker'
				if os.path.exists(executable):
					try:
						subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
					except Exception:
						pass

			self.finished_ok.emit()
		except Exception as e:
			# attempt restore (best-effort)
			try:
				for f in os.listdir(backup_dir):
					src = os.path.join(backup_dir, f)
					if os.path.isfile(src):
						shutil.copy2(src, f)
			except Exception:
				pass
			self.error.emit(str(e))


# helpers
def detect_platform_names():
	sysplat = platform.system().lower()
	names = []
	if 'windows' in sysplat:
		names += ['windows-x64', 'windows']
	elif 'linux' in sysplat:
		names += ['linux-x64', 'linux']
	elif 'darwin' in sysplat or 'mac' in sysplat:
		names += ['macos-x64', 'macos']
	names += ['knosthalij', 'danenone']
	out = []
	seen = set()
	for n in names:
		if n not in seen:
			seen.add(n)
			out.append(n)
	return out


def leer_version(path: str) -> str:
	try:
		if not os.path.exists(path):
			return ''
		tree = ET.parse(path)
		return tree.getroot().findtext('version', '')
	except Exception:
		return ''


def leer_version_remota() -> str:
	try:
		r = requests.get(REMOTE_XML, timeout=10)
		if r.status_code != 200:
			return ''
		root = ET.fromstring(r.text)
		return root.findtext('version', '')
	except Exception:
		return ''


def github_get_release_info(version: str) -> Tuple[Optional[dict], bool]:
	"""Return (release_json or None, release_found_bool)

	Uses the GitHub releases/tags API. Unauthenticated—rate limits may apply.
	"""
	api = f'https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{version}'
	try:
		r = requests.get(api, timeout=8)
		if r.status_code == 200:
			return r.json(), True
		return None, False
	except Exception:
		return None, False


def github_get_asset_download_url(version: str, plataforma: str) -> Tuple[Optional[str], bool]:
	"""Return (asset_url, release_found_bool).

	If release exists but no asset for platform, returns (None, True).
	If release doesn't exist, returns (None, False).
	"""
	rel, found = github_get_release_info(version)
	if not found:
		return None, False
	assets = rel.get('assets', []) if rel else []
	target = f'packagemaker-{version}-{plataforma}.zip'
	for a in assets:
		if a.get('name', '') == target:
			return a.get('browser_download_url'), True
	return None, True


def get_source_archive_for_version(version: str) -> Optional[str]:
	"""Return a URL to a source zip for the version tag if present, or to main branch archive as fallback."""
	tag_url = f'https://github.com/{GITHUB_REPO}/archive/refs/tags/{version}.zip'
	try:
		r = requests.head(tag_url, timeout=6)
		if r.status_code == 200:
			return tag_url
	except Exception:
		pass
	# fallback to main branch archive
	return f'https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip'


def send_native_notification(title: str, msg: str) -> bool:
	"""Best-effort native notification (Windows toast via win10toast_click, or notify2 on Linux).

	Returns True if a native-notification was attempted successfully.
	"""
	# Windows: try win10toast_click first (simple), then winotify (richer)
	if os.name == 'nt':
		if _win10toaster:
			try:
				_win10toaster.show_toast(title, msg, duration=6, threaded=True)
				return True
			except Exception:
				pass
		if _winotify:
			try:
				# winotify requires building a Notification object and calling .show()
				n = _winotify(app_id='Packagemaker', title=title, msg=msg, duration='short')
				try:
					n.set_audio(WinAudio.Default, loop=False)
				except Exception:
					pass
				n.show()
				return True
			except Exception:
				pass
	# Linux: notify2 (libnotify via DBus)
	if 'notify2' in globals() and notify2:
		global _notify2_inited
		try:
			if not _notify2_inited:
				notify2.init('packagemaker')
				_notify2_inited = True
			n = notify2.Notification(title, msg)
			n.set_timeout(4000)
			n.show()
			return True
		except Exception:
			pass
	return False


class UpdaterWindow(QtWidgets.QWidget):
	on_update_available = None
	on_install_started = None
	on_install_finished = None

	def __init__(self):
		super().__init__(None, QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.setWindowTitle('Packagemaker Updater')
		self.resize(560, 340)

		self.main = QtWidgets.QFrame(self)
		self.main.setObjectName('main')
		self.main.setGeometry(0, 0, 560, 340)

		self.status_label = QtWidgets.QLabel('Iniciando verificación...', self.main)
		self.status_label.setGeometry(16, 16, 520, 40)

		self.detail_text = QtWidgets.QTextEdit(self.main)
		self.detail_text.setGeometry(16, 64, 520, 200)
		self.detail_text.setReadOnly(True)

		self.install_btn = QtWidgets.QPushButton('Instalar', self.main)
		self.install_btn.setGeometry(420, 274, 100, 40)
		self.install_btn.setEnabled(False)
		self.install_btn.clicked.connect(self._install_clicked)

		self.later_btn = QtWidgets.QPushButton('Ahora no', self.main)
		self.later_btn.setGeometry(312, 274, 100, 40)
		self.later_btn.clicked.connect(self.close)

		self.notify_cb = QtWidgets.QCheckBox('Notificarme', self.main)
		self.notify_cb.setGeometry(16, 276, 140, 22)
		self.notify_cb.setChecked(True)

		self.auto_cb = QtWidgets.QCheckBox('Descarga automática', self.main)
		self.auto_cb.setGeometry(168, 276, 160, 22)
		self.auto_cb.setChecked(False)

		self.progress = QtWidgets.QProgressBar(self.main)
		self.progress.setGeometry(16, 308, 504, 14)
		self.progress.setValue(0)

		# Threads
		self.checker = UpdateChecker(interval=180)
		self.checker.update_found.connect(self._on_update_found)
		self.checker.status.connect(self._set_status)
		self.checker.error.connect(self._set_error)
		self.checker.start()

		self.release_url = None
		self.current_version = leer_version(LOCAL_XML) or 'desconocida'

		QtCore.QTimer.singleShot(80, self.place_bottom_right)

	def place_bottom_right(self):
		screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
		x = screen.x() + screen.width() - self.width() - 20
		y = screen.y() + screen.height() - self.height() - 40
		self.move(x, y)

	def _set_status(self, txt: str):
		self.status_label.setText(txt)

	def _set_error(self, txt: str):
		self.status_label.setText(f'Error: {txt}')

	def _on_update_found(self, version: str, plataforma: str):
		"""When checker signals an update, verify on GitHub and prompt accordingly."""
		self.status_label.setText(f'Versión remota: {version} detectada')
		self.detail_text.setPlainText('Obteniendo información del release...')

		# Ask GitHub: is there a release with that tag? does it contain an asset for our platform?
		asset_url, release_found = github_get_asset_download_url(version, plataforma)

		# Always try to send a native notification (best-effort)
		if self.notify_cb.isChecked():
			send_native_notification('Packagemaker: actualización disponible', f'Versión {version} detectada')

		# Read remote notes if available
		try:
			r = requests.get(REMOTE_XML, timeout=8)
			if r.status_code == 200:
				root = ET.fromstring(r.text)
				notes = root.findtext('notes') or root.findtext('changelog') or ''
				if notes:
					self.detail_text.setPlainText(notes)
				else:
					self.detail_text.setPlainText(f'Versión {version} disponible para {plataforma}.')
		except Exception:
			self.detail_text.setPlainText(f'Versión {version} disponible para {plataforma}.')

		# notify host app
		if callable(self.on_update_available):
			try:
				self.on_update_available(version, plataforma)
			except Exception:
				pass

		# If GitHub release contains a platform asset -> ask to download and install
		if asset_url:
			self.release_url = asset_url
			self.install_btn.setEnabled(True)
			# interactive prompt (non-blocking modal) — use QMessageBox to allow action buttons
			answer = QtWidgets.QMessageBox.question(self, 'Actualizar',
													f'Se encontró una release binaria para {plataforma}.\n¿Descargar e instalar la versión {version}?',
													QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
			if answer == QtWidgets.QMessageBox.Yes:
				if self.auto_cb.isChecked():
					self._install_clicked()
				else:
					self._install_clicked()
			else:
				# user declined – keep the button enabled for manual install
				pass
			return

		# If release exists but no binary for this platform
		if release_found and not asset_url:
			answer = QtWidgets.QMessageBox.question(self, 'Release sin binario',
													'El release existe pero no contiene un binario para tu plataforma.\n¿Instalar la versión de fuente (BETA-DEV)?',
													QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
			if answer == QtWidgets.QMessageBox.Yes:
				src = get_source_archive_for_version(version)
				if src:
					self.release_url = src
					self._install_clicked()
				else:
					QtWidgets.QMessageBox.information(self, 'No disponible', 'No se pudo localizar el archivo fuente.')
			return

		# No release tag found at all -> offer source install
		if not release_found:
			answer = QtWidgets.QMessageBox.question(self, 'Sin release',
													'No existe un release en GitHub para esa versión.\n¿Instalar la versión de fuente (BETA-DEV)?',
													QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
			if answer == QtWidgets.QMessageBox.Yes:
				src = get_source_archive_for_version(version)
				if src:
					self.release_url = src
					self._install_clicked()
				else:
					QtWidgets.QMessageBox.information(self, 'No disponible', 'No se pudo localizar el archivo fuente.')
			return

	def _install_clicked(self):
		if not self.release_url:
			self._set_status('URL de release no encontrada')
			return
		self.install_btn.setEnabled(False)
		if callable(self.on_install_started):
			try:
				self.on_install_started()
			except Exception:
				pass

		self.dl = DownloadWorker(self.release_url)
		self.dl.progress.connect(self._on_progress)
		self.dl.status.connect(self._set_status)
		self.dl.finished_ok.connect(self._on_install_success)
		self.dl.error.connect(self._on_install_error)
		self.dl.start()

	def _on_progress(self, pct: int):
		self.progress.setValue(pct)

	def _on_install_success(self):
		self._set_status('Actualización instalada correctamente.')
		if callable(self.on_install_finished):
			try:
				self.on_install_finished(True)
			except Exception:
				pass
		QtCore.QTimer.singleShot(1200, self.close)

	def _on_install_error(self, msg: str):
		self._set_status(f'Error instalando: {msg}')
		if callable(self.on_install_finished):
			try:
				self.on_install_finished(False)
			except Exception:
				pass
		self.install_btn.setEnabled(True)


def main():
	app = QtWidgets.QApplication(sys.argv)
	# small QSS
	qss = '''
	QWidget { background: #071216; color: #dfeee6; }
	QPushButton { background: #2b6ef6; color: white; border-radius:6px; padding:6px }
	QProgressBar { background: #0b1220; color:#dbeee6; border: 1px solid #12232b; border-radius:6px; height:10px }
	QTextEdit { background: #08131a; color:#dbeee6 }
	'''
	app.setStyleSheet(qss)

	w = UpdaterWindow()

	def cb_update_available(v, p):
		print('Update available', v, p)

	def cb_install_started():
		print('Install started')

	def cb_install_finished(success):
		print('Install finished', success)

	w.on_update_available = cb_update_available
	w.on_install_started = cb_install_started
	w.on_install_finished = cb_install_finished

	# First-run: send a one-time desktop test notification using native library if possible
	try:
		test_flag = os.path.join(os.path.expanduser('~'), '.packagemaker_notif_tested')
		if not os.path.exists(test_flag):
			# best-effort; do not block startup on failure
			send_native_notification('Packagemaker', 'Notificación de prueba: escritorio configurado para Packagemaker')
			try:
				open(test_flag, 'w').close()
			except Exception:
				pass
	except Exception:
		pass

	w.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()


