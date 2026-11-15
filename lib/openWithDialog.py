# -*- coding: utf-8 -*-
"""Compatibility shim for OpenWithDialog.

The dialog historically lived under lib/.walkcube; tests and callers import it
from lib.openWithDialog, so keep a thin re-export layer here.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_module_path = Path(__file__).resolve().parent / ".walkcube" / "openWithDialog.py"

if _module_path.exists():
    spec = importlib.util.spec_from_file_location("_compat_openwithdialog", _module_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        for name in dir(module):
            if name.startswith("__") and name not in {"__doc__", "__file__", "__name__"}:
                continue
            globals()[name] = getattr(module, name)
    else:
        raise ImportError(f"Could not load OpenWithDialog from {_module_path}")
else:
    raise ImportError(f"OpenWithDialog not found at {_module_path}")
