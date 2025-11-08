# ---------- NOTIFICACIÓN QT ----------
def is_dark_mode():
    sistema = platform.system().lower()
    if "windows" in sistema:
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return val == 0
        except Exception:
            return False
    elif "linux" in sistema:
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        if "dark" in desktop or "plasma" in desktop:
            return True
    return False


def get_chromium_qss(dark=False):
    if dark:
        return """
        QWidget#notifBG {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #202124, stop:1 #303134);
            border: 1px solid #5f6368;
            border-radius: 12px;
            color: #e8eaed;
            font-family: 'Segoe UI','Roboto','Arial',sans-serif;
        }
        QLabel#titleLabel { font-weight:600; font-size:15px; color:#e8eaed; }
        QTextBrowser#body { border:none; background:transparent; color:#e8eaed; }
        QProgressBar { height:10px; border-radius:6px; background:#3c4043; color:#e8eaed; }
        QProgressBar::chunk { background-color:#8ab4f8; border-radius:6px; }
        QPushButton#acceptBtn { background:transparent; color:#8ab4f8; border:none; padding:6px; }
        QPushButton#acceptBtn:hover { background:rgba(138,180,248,0.1); border-radius:6px; }
        """
    else:
        return """
        QWidget#notifBG {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ffffff, stop:1 #f1f3f4);
            border: 1px solid #dfe3e6;
            border-radius: 12px;
            color: #202124;
            font-family: 'Segoe UI','Roboto','Arial',sans-serif;
        }
        QLabel#titleLabel { font-weight:600; font-size:15px; color:#202124; }
        QTextBrowser#body { border:none; background:transparent; color:#3c4043; }
        QProgressBar { height:10px; border-radius:6px; background:#dadce0; }
        QProgressBar::chunk { background-color:#1a73e8; border-radius:6px; }
        QPushButton#acceptBtn { background:transparent; color:#1a73e8; border:none; padding:6px; }
        QPushButton#acceptBtn:hover { background:rgba(26,115,232,0.06); border-radius:6px; }
        """


class ChromiumNotification(QtWidgets.QWidget):
    closed_signal = QtCore.pyqtSignal(object)

    def __init__(self, title, body_md, progress=False, buttons=None, icon=None, timeout=None, parent=None):
        super().__init__(parent)
        self.setObjectName("notifBG")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet(get_chromium_qss(is_dark_mode()))

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Icono
        icon_label = QtWidgets.QLabel()
        icon_label.setFixedSize(42, 42)
        if icon and os.path.isfile(icon):
            pix = QtGui.QPixmap(icon).scaled(42, 42, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        else:
            pix = QtGui.QPixmap(42, 42)
            pix.fill(QtCore.Qt.transparent)
            p = QtGui.QPainter(pix)
            p.setBrush(QtGui.QColor("#8ab4f8" if is_dark_mode() else "#c8dafc"))
            p.setPen(QtCore.Qt.NoPen)
            p.setRenderHint(QtGui.QPainter.Antialiasing)
            p.drawEllipse(0, 0, 42, 42)
            p.end()
        icon_label.setPixmap(pix)
        layout.addWidget(icon_label)

        v = QtWidgets.QVBoxLayout()
        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setObjectName("titleLabel")
        v.addWidget(title_lbl)

        self.body = QtWidgets.QTextBrowser()
        self.body.setObjectName("body")
        self.body.setHtml(markdown_to_html(body_md))
        self.body.setOpenExternalLinks(True)
        self.body.setMaximumHeight(140)
        v.addWidget(self.body)

        self.progress = None
        if progress:
            self.progress = QtWidgets.QProgressBar()
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            v.addWidget(self.progress)

        if buttons:
            h = QtWidgets.QHBoxLayout()
            h.addStretch()
            for text, role in buttons:
                btn = QtWidgets.QPushButton(text)
                btn.setObjectName("acceptBtn")
                btn.setCursor(QtCore.Qt.PointingHandCursor)
                btn.clicked.connect(lambda _, r=role: self._handle_click(r))
                h.addWidget(btn)
            v.addLayout(h)

        layout.addLayout(v)
        self._callback = None
        self._anim = None

        if timeout:
            QtCore.QTimer.singleShot(timeout, self.fade_out)

    def fade_in(self):
        self.setWindowOpacity(0)
        self.show()
        self._anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(350)
        self._anim.setStartValue(0)
        self._anim.setEndValue(1)
        self._anim.start()

    def fade_out(self):
        self._anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(400)
        self._anim.setStartValue(1)
        self._anim.setEndValue(0)
        self._anim.finished.connect(self._on_close)
        self._anim.start()

    def _on_close(self):
        self.close()
        self.closed_signal.emit(self)

    def _handle_click(self, role):
        if self._callback:
            self._callback(role, self)
        self.fade_out()

    def on_click(self, callback):
        self._callback = callback

    def set_progress(self, pct: int):
        if self.progress:
            self.progress.setValue(int(pct))
            QtWidgets.QApplication.processEvents()


# ---------- ADMINISTRADOR DE NOTIFICACIONES ----------
class NotificationManager:
    _instance = None
    _margin = 15

    def __init__(self):
        self.notifications = []

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def show(self, notif: ChromiumNotification):
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        notif_height = notif.sizeHint().height()
        y = screen.height() - notif_height - self._margin

        # reposicionar notificaciones anteriores
        for n in self.notifications:
            y -= n.height() + self._margin

        x = screen.width() - notif.sizeHint().width() - self._margin
        notif.move(x, y)
        notif.closed_signal.connect(lambda n=notif: self.remove(n))
        notif.fade_in()
        self.notifications.append(notif)

    def remove(self, notif):
        if notif in self.notifications:
            self.notifications.remove(notif)
            self.reposition()

    def reposition(self):
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        y = screen.height() - self._margin
        for n in reversed(self.notifications):
            y -= n.height() + self._margin
            x = screen.width() - n.width() - self._margin
            n.move(x, y)
