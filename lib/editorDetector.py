# -*- coding: utf-8 -*-
"""Compatibility wrapper for the legacy editor detector used by the WalkCube dialogs."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_module_path = Path(__file__).resolve().parent / ".walkcube" / "editorDetector.py"

if not _module_path.exists():
    raise ImportError(f"EditorDetector not found at {_module_path}")

_spec = importlib.util.spec_from_file_location("lib._walkcube.editorDetector", _module_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load EditorDetector from {_module_path}")

_module = importlib.util.module_from_spec(_spec)
_sys_package = sys.modules.get("lib")
if _sys_package is not None and getattr(_sys_package, "__path__", None) is not None:
    sys.modules.setdefault("lib._walkcube", type(sys)("lib._walkcube"))
    sys.modules["lib._walkcube"].__path__ = [str(_module_path.parent)]
    sys.modules["lib._walkcube"] = sys.modules.get("lib._walkcube", _module)

sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)

for _name in dir(_module):
    if _name.startswith("__") and _name not in {"__doc__", "__file__", "__name__"}:
        continue
    globals()[_name] = getattr(_module, _name)
