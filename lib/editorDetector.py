# -*- coding: utf-8 -*-
"""Compatibility shim for the legacy editor detector used by the WalkCube dialogs.

Aliases ``lib.editorDetector`` to the real module object (see
``lib/openWithDialog.py`` for why copying names breaks attribute patching).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_module_path = Path(__file__).resolve().parent / ".walkcube" / "editorDetector.py"
if not _module_path.exists():
    raise ImportError(f"EditorDetector not found at {_module_path}")

_pkg = sys.modules.get("lib._walkcube")
if _pkg is None:
    _pkg = type(sys)("lib._walkcube")
    _pkg.__path__ = [str(_module_path.parent)]
    sys.modules["lib._walkcube"] = _pkg

_spec = importlib.util.spec_from_file_location("lib._walkcube.editorDetector", _module_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load EditorDetector from {_module_path}")

_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)
sys.modules[__name__] = _module
