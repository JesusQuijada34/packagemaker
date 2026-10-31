# -*- coding: utf-8 -*-
"""Canal único de reporte para la interfaz.

Todo aviso se publica en dos sitios a la vez:

- la **barra de estado** inferior, que guarda el último mensaje sin interrumpir;
- un **diálogo modal con botón OK**, para que la información, la advertencia o el
  error se lean con calma y se cierren cuando el usuario termine.

Así el mensaje no se pierde en una etiqueta que se sobreescribe y el usuario
siempre tiene un botón explícito para cerrar.
"""

from __future__ import annotations

from typing import Callable, Optional


# Modos válidos de ``AlertDialog``; se mapean a un icono y color propios.
_MODES = {"info", "success", "warning", "error", "question"}


class Reporter:
    """Publica avisos en la barra de estado y en un diálogo con OK."""

    def __init__(
        self,
        status_bar=None,
        dialog_parent=None,
        dialog_launcher: Optional[Callable] = None,
    ):
        self._status_bar = status_bar
        self._dialog_parent = dialog_parent
        self._dialog_launcher = dialog_launcher
        self.last_message: str = ""

    # -- configuración tardía ----------------------------------------
    def attach_status_bar(self, status_bar) -> None:
        self._status_bar = status_bar

    def attach_dialog_launcher(self, launcher: Callable) -> None:
        """``launcher(parent, title, message, mode, buttons)``."""
        self._dialog_launcher = launcher

    # -- API pública --------------------------------------------------
    def info(self, title: str, message: str, *, dialog: bool = False) -> None:
        self._publish("info", title, message, dialog=dialog)

    def success(self, title: str, message: str, *, dialog: bool = False) -> None:
        self._publish("success", title, message, dialog=dialog)

    def warning(self, title: str, message: str, *, dialog: bool = True) -> None:
        self._publish("warning", title, message, dialog=dialog)

    def error(self, title: str, message: str, *, dialog: bool = True) -> None:
        self._publish("error", title, message, dialog=dialog)

    def notify(self, message: str) -> None:
        """Sólo barra de estado: para progreso continuo, sin abrir diálogos."""
        self.last_message = str(message)
        self._show_status(str(message))

    def progress(self, message: str) -> None:
        """Alias de ``notify`` con nombre acorde al uso durante una compilación."""
        self.notify(message)

    def _publish(self, mode: str, title: str, message: str, *, dialog: bool) -> None:
        if mode not in _MODES:
            mode = "info"
        self.last_message = f"{title}: {message}" if title else str(message)
        self._show_status(self.last_message)
        if dialog:
            self._show_dialog(title, message, mode)

    def _show_status(self, message: str) -> None:
        bar = self._status_bar
        if bar is None:
            return
        try:
            bar.showMessage(message)
        except Exception:
            pass

    def _show_dialog(self, title: str, message: str, mode: str) -> None:
        launcher = self._dialog_launcher
        if launcher is None:
            return
        try:
            launcher(self._dialog_parent, title, message, mode=mode)
        except Exception:
            pass


def classify_build_message(message: str) -> str:
    """Deduce el modo de un mensaje de log del compilador.

    ``[ERROR]``/``❌`` → error, ``[WARN]`` → advertencia, ``[SUCCESS]``/``✅``
    → éxito, cualquier otra cosa → progreso (sin diálogo).
    """
    text = str(message or "")
    upper = text.upper()
    if "[ERROR]" in upper or text.startswith("❌") or "ERROR:" in upper:
        return "error"
    if "[WARN]" in upper or "⚠" in text:
        return "warning"
    if "[SUCCESS]" in upper or "✅" in text:
        return "success"
    return "info"
