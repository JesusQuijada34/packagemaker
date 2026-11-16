# -*- coding: utf-8 -*-
"""Compatibility shim for OpenWithDialog.

The dialog historically lived under lib/.walkcube. This shim loads that module
and then **aliases itself to it in ``sys.modules``**, so ``lib.openWithDialog``
*is* the real module object. Copying the names into this namespace would break
``unittest.mock.patch("lib.openWithDialog.<name>")``: the patched attribute would
land on the shim while the functions keep resolving names in the real module.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_module_path = Path(__file__).resolve().parent / ".walkcube" / "openWithDialog.py"
if not _module_path.exists():
    raise ImportError(f"OpenWithDialog not found at {_module_path}")

_pkg = sys.modules.get("lib._walkcube")
if _pkg is None:
    _pkg = type(sys)("lib._walkcube")
    _pkg.__path__ = [str(_module_path.parent)]
    sys.modules["lib._walkcube"] = _pkg

_spec = importlib.util.spec_from_file_location("lib._walkcube.openWithDialog", _module_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load OpenWithDialog from {_module_path}")

_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)
sys.modules[__name__] = _module
