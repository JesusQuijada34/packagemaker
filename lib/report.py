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

# Términos que delatan la línea útil de un log largo (tracebacks, errores de
# compilador, fallos de Python). Se buscan sin distinguir mayúsculas.
_ERROR_TERMS = (
    "error",
    "traceback",
    "exception",
    "failed",
    "fallo",
    "falló",
    "no se pudo",
    "no se encontró",
    "cannot",
    "not found",
    "permission denied",
    "refused",
    "timeout",
    "fatal",
)

# Cuántas líneas significativas se conservan como máximo en el resumen.
_SUMMARY_MAX_LINES = 6
# Por debajo de estos umbrales el mensaje ya es legible y no se resume.
_SUMMARY_MAX_CHARS = 400
_SUMMARY_MAX_LINES_RAW = 6


def summarize_message(message: str, *, max_lines: int = _SUMMARY_MAX_LINES) -> str:
    """Condensa un mensaje largo en sus líneas relevantes.

    Los logs del compilador o los ``traceback`` de Python pueden ocupar cientos
    de líneas y no caben en un diálogo. Si el mensaje es corto se devuelve tal
    cual; si es largo se conservan, en orden, las líneas que contienen términos
    de error (``ERROR``, ``Traceback``, ``Exception``...) y se antepone un aviso
    con cuántas líneas se omitieron. Sin coincidencias se devuelven la primera y
    la última línea, que suelen enmarcar el fallo.
    """
    text = str(message or "").strip()
    if not text:
        return text
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if len(lines) <= _SUMMARY_MAX_LINES_RAW and len(text) <= _SUMMARY_MAX_CHARS:
        return text

    matched = [line for line in lines if any(term in line.lower() for term in _ERROR_TERMS)]
    if matched:
        picked = matched[:max_lines]
        if len(matched) > max_lines:
            picked = picked[: max_lines - 1] + [
                f"... ({len(matched) - (max_lines - 1)} líneas de error más)"
            ]
    else:
        head = lines[0]
        tail = lines[-1] if len(lines) > 1 else ""
        picked = [head] if not tail else [head, "...", tail]

    omitted = max(0, len(lines) - len(picked))
    summary = "\n".join(picked)
    if omitted:
        summary = f"({omitted} líneas omitidas; resumen del error)\n{summary}"
    return summary


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
        # Un error largo (log de compilador, traceback) no cabe en el diálogo:
        # se resume a sus líneas significativas antes de mostrarlo.
        detail = summarize_message(message) if mode in ("error", "warning") else message
        try:
            launcher(self._dialog_parent, title, detail, mode=mode)
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
