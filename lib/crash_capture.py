# -*- coding: utf-8 -*-
"""Captura global de fallos, incluidos los que ocurren antes de la interfaz.

``sys.excepthook`` sólo cubre el hilo principal y se instala tarde si la
aplicación revienta al importar módulos de arranque. Por eso ``install()`` se
llama lo antes posible en ``main()`` y cubre además los hilos y los avisos de
Qt.

Cuando un fallo ocurre sin ventana no hay dónde preguntar: el reporte se
**encola** y la página de Reportes lo muestra al abrirse. Nada se envía a
GitHub sin sesión iniciada.
"""

from __future__ import annotations

import sys
import threading
import traceback
from typing import Dict

from lib import github_issue_reporter, report_queue, report_telemetry

_installed = False
_context = "arranque"
_handlers: list = []


def set_context(context: str) -> None:
    """Etiqueta el momento actual (``arranque``, ``interfaz``, ``build``…)."""
    global _context
    _context = str(context or "arranque")


def context() -> str:
    return _context


def _describe(exc_type: type, exc_value: BaseException) -> Dict[str, str]:
    name = getattr(exc_type, "__name__", str(exc_type))
    message = report_telemetry.sanitize(str(exc_value))
    return {
        "title": f"[auto] {name}: {message}"[:240],
        "kind": name,
        "message": message,
        "fingerprint": report_telemetry.fingerprint(name, message),
    }


def auto_report_enabled() -> bool:
    """El usuario puede desactivar el envío automático desde la página."""
    try:
        from lib.pm_data import get_pm_data

        return bool(get_pm_data().get_user("auto_report_errors", True))
    except Exception:
        return True


def capture(exc_type: type, exc_value: BaseException, exc_tb, *, where: str = "") -> None:
    """Registra el fallo: lo envía si hay sesión y si no, lo encola.

    Nunca propaga una excepción: si el reporte falla, el fallo original sigue
    su curso normal.
    """
    try:
        info = _describe(exc_type, exc_value)
        where = where or _context
        traceback_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

        if report_queue.already_sent(info["fingerprint"]):
            return

        if auto_report_enabled() and github_issue_reporter.has_session():
            result = github_issue_reporter.report_exception(
                exc_type, exc_value, exc_tb, context=where
            )
            if result.ok:
                report_queue.record_sent(info["fingerprint"])
                return

        # Sin sesión, sin red o con la API rechazando: se guarda para la página.
        report_queue.enqueue(
            {
                "title": info["title"],
                "description": (
                    f"Excepción no controlada durante {where}.\n\n"
                    f"{info['kind']}: {info['message']}"
                ),
                "kind": info["kind"],
                "fingerprint": info["fingerprint"],
                "traceback": report_telemetry.sanitize(traceback_text),
                "environment": report_telemetry.collect_environment(),
                "auto": True,
            }
        )
    except Exception:
        pass


def _excepthook(exc_type, exc_value, exc_tb) -> None:
    capture(exc_type, exc_value, exc_tb)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def _thread_excepthook(args) -> None:
    if args.exc_type is SystemExit:
        return
    capture(
        args.exc_type,
        args.exc_value,
        args.exc_traceback,
        where=f"hilo {getattr(args.thread, 'name', '?')}",
    )
    threading.__excepthook__(args)


def install() -> None:
    """Engancha los manejadores una sola vez."""
    global _installed
    if _installed:
        return
    _installed = True

    sys.excepthook = _excepthook
    try:
        threading.excepthook = _thread_excepthook
    except Exception:
        pass
    _install_qt_handler()


def _install_qt_handler() -> None:
    """Convierte los avisos críticos de Qt en reportes.

    Qt escribe sus errores en stderr y no lanza excepción, así que un fallo de
    pintado o de carga de recursos pasaba desapercibido.
    """
    try:
        from PyQt6.QtCore import QtMsgType, qInstallMessageHandler
    except Exception:
        return

    def _handler(mode, msg_context, message):
        try:
            if mode in (QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg):
                text = report_telemetry.sanitize(str(message))
                report_queue.enqueue(
                    {
                        "title": f"[qt] {text}"[:240],
                        "description": f"Aviso crítico de Qt:\n\n{text}",
                        "kind": "QtMessage",
                        "fingerprint": report_telemetry.fingerprint("QtMessage", text),
                        "environment": report_telemetry.collect_environment(),
                        "auto": True,
                    }
                )
        except Exception:
            pass
        _handlers.append(message)

    try:
        qInstallMessageHandler(_handler)
    except Exception:
        pass


def reset_for_tests() -> None:
    """Permite a los tests reinstalar los hooks entre casos."""
    global _installed, _context, _handlers
    _installed = False
    _context = "arranque"
    _handlers = []
