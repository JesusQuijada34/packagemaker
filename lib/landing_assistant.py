# -*- coding: utf-8 -*-
"""Asistente lateral del landing de login (Fase 3.3 de bugs.txt).

Dos enlaces expanden la tarjeta hacia la derecha con un panel de guía paso a
paso:

* Flujo A — "¿No posees un token de GitHub?": pasos para crear un token.
* Flujo B — "¿No tienes una cuenta de GitHub?": pasos para registrarse.

El panel se anima con un ``QPropertyAnimation`` sobre el ancho de la tarjeta y
el enlace cambia de texto ("¿Ya obtuviste tu token?", "¿Ya posees una cuenta?")
para plegar la vista y restaurar el estado original sin dejar el layout roto.

El módulo detecta además el navegador predeterminado del sistema para
personalizar las instrucciones. Sólo usa la biblioteca estándar + PyQt6.
"""
from __future__ import annotations

import shutil
import sys

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    QWidget = object

from lib.i18n import tr

PANEL_WIDTH = 360
ANIMATION_MS = 320


def _browser_from_windows_registry() -> str:
    try:
        import winreg  # type: ignore
    except ImportError:
        return ""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\Shell\Associations"
            r"\UrlAssociations\http\UserChoice",
        )
        with key:
            prog_id, _ = winreg.QueryValueEx(key, "ProgId")
    except OSError:
        return ""
    mapping = {
        "MSEdgeHTM": "Microsoft Edge",
        "ChromeHTML": "Google Chrome",
        "FirefoxURL": "Mozilla Firefox",
        "OperaStable": "Opera",
        "BraveHTML": "Brave",
        "VivaldiHTM": "Vivaldi",
    }
    return mapping.get(str(prog_id), str(prog_id))


def _browser_from_linux_desktop() -> str:
    for tool in ("xdg-settings", "xdg-mime"):
        path = shutil.which(tool)
        if not path:
            continue
        try:
            import subprocess

            if tool == "xdg-settings":
                out = subprocess.run(
                    [path, "get", "default-web-browser"],
                    capture_output=True, text=True, timeout=3,
                )
            else:
                out = subprocess.run(
                    [path, "query", "default", "x-scheme-handler/http"],
                    capture_output=True, text=True, timeout=3,
                )
            value = (out.stdout or "").strip()
        except (OSError, subprocess.SubprocessError):
            continue
        if value:
            name = value.split(".desktop")[0]
            return name.replace("-", " ").replace("_", " ").title()
    return ""


def detect_default_browser() -> str:
    """Nombre legible del navegador predeterminado, o cadena vacía.

    Es un mejor esfuerzo: en un entorno sin escritorio (CI) devuelve ``""`` y el
    asistente usa un texto genérico.
    """
    if sys.platform.startswith("win"):
        name = _browser_from_windows_registry()
        if name:
            return name
    elif sys.platform == "darwin":
        return "Safari"
    else:
        name = _browser_from_linux_desktop()
        if name:
            return name
    for candidate, label in (
        ("microsoft-edge", "Microsoft Edge"),
        ("google-chrome", "Google Chrome"),
        ("chromium", "Chromium"),
        ("firefox", "Mozilla Firefox"),
    ):
        if shutil.which(candidate):
            return label
    return ""


class LandingAssistant(QWidget):
    """Panel lateral desplegable con la guía paso a paso."""

    def __init__(self, parent=None, browser_name: str = ""):
        super().__init__(parent)
        self._browser = browser_name or detect_default_browser()
        self._flow = ""
        self._step = 0
        self._steps: list[str] = []

        self.setObjectName("GitHubAssistantPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(14)

        self.heading = QLabel(self)
        self.heading.setObjectName("GitHubAssistantHeading")
        self.heading.setWordWrap(True)
        layout.addWidget(self.heading)

        self.body = QLabel(self)
        self.body.setObjectName("GitHubAssistantBody")
        self.body.setWordWrap(True)
        self.body.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.body, 1)

        nav = QHBoxLayout()
        self.back_button = QPushButton(tr("github.assistant_back"), self)
        self.back_button.setObjectName("GitHubAssistantBack")
        self.back_button.clicked.connect(self._previous_step)
        nav.addWidget(self.back_button)
        self.next_button = QPushButton(tr("github.assistant_next"), self)
        self.next_button.setObjectName("GitHubAssistantNext")
        self.next_button.clicked.connect(self._next_step)
        nav.addWidget(self.next_button)
        layout.addLayout(nav)

        self._render()
        self.setFixedWidth(PANEL_WIDTH)

    # ── flujos ────────────────────────────────────────────────────────────
    def _token_steps(self) -> list[str]:
        browser = self._browser or tr("github.assistant_browser_generic")
        return [
            tr("github.assistant_token_step1").format(browser=browser),
            tr("github.assistant_token_step2"),
            tr("github.assistant_token_step3"),
        ]

    def _account_steps(self) -> list[str]:
        browser = self._browser or tr("github.assistant_browser_generic")
        return [
            tr("github.assistant_account_step1").format(browser=browser),
            tr("github.assistant_account_step2"),
            tr("github.assistant_account_step3"),
        ]

    def start_flow(self, flow: str) -> None:
        """Abre el flujo ``token`` o ``account`` desde el primer paso."""
        self._flow = flow
        self._step = 0
        self._steps = self._token_steps() if flow == "token" else self._account_steps()
        self.heading.setText(
            tr("github.assistant_token_title")
            if flow == "token"
            else tr("github.assistant_account_title")
        )
        self._render()

    def _render(self) -> None:
        if not self._steps:
            return
        self.body.setText(self._steps[self._step])
        self.back_button.setEnabled(self._step > 0)
        self.next_button.setText(
            tr("github.assistant_done")
            if self._step >= len(self._steps) - 1
            else tr("github.assistant_next")
        )

    def _next_step(self) -> None:
        if self._step < len(self._steps) - 1:
            self._step += 1
            self._render()

    def _previous_step(self) -> None:
        if self._step > 0:
            self._step -= 1
            self._render()
