# -*- coding: utf-8 -*-
"""Cola local de reportes pendientes.

Un fallo puede ocurrir sin conexión, sin sesión de GitHub o antes de que exista
la ventana. En esos casos el reporte no se pierde: se guarda en
``data/report_queue.json`` y la página de Reportes lo reintenta.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

_MAX_ENTRIES = 50
_QUEUE_NAME = "report_queue.json"


def _queue_path() -> Path:
    try:
        from lib.pm_data import pm_data_path

        return pm_data_path().with_name(_QUEUE_NAME)
    except Exception:
        return Path(__file__).resolve().parent.parent / "data" / _QUEUE_NAME


def _read() -> List[Dict[str, Any]]:
    path = _queue_path()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return raw if isinstance(raw, list) else []


def _write(entries: List[Dict[str, Any]]) -> bool:
    path = _queue_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(entries[-_MAX_ENTRIES:], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    except OSError:
        return False


def enqueue(entry: Dict[str, Any]) -> bool:
    """Guarda un reporte pendiente. Devuelve si se pudo persistir."""
    if not isinstance(entry, dict) or not entry.get("title"):
        return False
    entries = _read()
    entry = dict(entry)
    entry.setdefault("queued_at", time.time())
    entries.append(entry)
    return _write(entries)


def pending() -> List[Dict[str, Any]]:
    return _read()


def count() -> int:
    return len(_read())


def clear() -> None:
    _write([])


def remove(index: int) -> None:
    entries = _read()
    if 0 <= index < len(entries):
        del entries[index]
        _write(entries)


def take_all() -> List[Dict[str, Any]]:
    """Vacía la cola y devuelve lo que había (para reintentar el envío)."""
    entries = _read()
    if entries:
        _write([])
    return entries


def drain(sender) -> Dict[str, int]:
    """Reintenta cada pendiente con ``sender(entry) -> bool``.

    Los que fallan se vuelven a encolar, así que un corte de red a mitad no
    pierde nada. Devuelve el recuento de enviados y fallidos.
    """
    entries = take_all()
    sent = failed = 0
    remaining: List[Dict[str, Any]] = []
    for entry in entries:
        try:
            ok = bool(sender(entry))
        except Exception:
            ok = False
        if ok:
            sent += 1
        else:
            failed += 1
            remaining.append(entry)
    if remaining:
        _write(_read() + remaining)
    return {"sent": sent, "failed": failed}


def record_sent(fingerprint: str) -> None:
    """Marca una huella como ya reportada (anti-duplicado entre sesiones)."""
    if not fingerprint:
        return
    try:
        store = _sent_store()
        data = json.loads(store.read_text(encoding="utf-8")) if store.exists() else {}
        if not isinstance(data, dict):
            data = {}
        data[fingerprint] = time.time()
        # Conserva sólo las 200 huellas más recientes.
        ordered = sorted(data.items(), key=lambda kv: kv[1], reverse=True)[:200]
        store.parent.mkdir(parents=True, exist_ok=True)
        store.write_text(json.dumps(dict(ordered), indent=2), encoding="utf-8")
    except (OSError, ValueError):
        pass


def _sent_store() -> Path:
    return _queue_path().with_name("report_sent.json")


def already_sent(fingerprint: str) -> bool:
    if not fingerprint:
        return False
    try:
        store = _sent_store()
        data = json.loads(store.read_text(encoding="utf-8")) if store.exists() else {}
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and fingerprint in data
