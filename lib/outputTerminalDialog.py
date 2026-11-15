# -*- coding: utf-8 -*-
"""Compatibility wrapper for the legacy terminal dialog kept under lib/.walkcube."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_module_path = Path(__file__).resolve().parent / ".walkcube" / "outputTerminalDialog.py"
if not _module_path.exists():
    raise ImportError(f"OutputTerminalDialog not found at {_module_path}")

_spec = importlib.util.spec_from_file_location("lib._walkcube.outputTerminalDialog", _module_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load OutputTerminalDialog from {_module_path}")

_module = importlib.util.module_from_spec(_spec)
_parent = sys.modules.get("lib._walkcube")
if _parent is None:
    _parent = type(sys)("lib._walkcube")
    _parent.__path__ = [str(_module_path.parent)]
    sys.modules["lib._walkcube"] = _parent

sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)

for _name in dir(_module):
    if _name.startswith("__") and _name not in {"__doc__", "__file__", "__name__"}:
        continue
    globals()[_name] = getattr(_module, _name)
