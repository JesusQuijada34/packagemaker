# -*- coding: utf-8 -*-
"""Regenera las capturas de la interfaz en ``assets/screenshots``.

Renderiza cada página en modo *offscreen* (sin abrir una ventana real) y guarda
una imagen por página con el nombre ``gui-N.png``. Sirve para mantener el README
al día tras cambios de interfaz.

Uso::

    QT_QPA_PLATFORM=offscreen python scripts/capture_screenshots.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "assets" / "screenshots"

# Orden de las páginas en el ``QStackedWidget`` de la ventana principal.
PAGES = ("create", "build", "config", "moonfix", "about")


def capture(window_width: int = 1280, window_height: int = 860) -> list[Path]:
    """Captura cada página y devuelve las rutas escritas."""
    from PyQt6.QtWidgets import QApplication

    import packagemaker as pm

    app = QApplication.instance() or QApplication(sys.argv[:1])
    window = pm.PackageTodoGUI()
    window.resize(window_width, window_height)
    window.show()
    app.processEvents()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for index in range(min(len(PAGES), window.stack.count())):
        window.stack.setCurrentIndex(index)
        for _ in range(3):
            app.processEvents()
        path = OUTPUT_DIR / f"gui-{index + 1}.png"
        window.grab().save(str(path))
        written.append(path)
    window.close()
    return written


def main() -> int:
    written = capture()
    for path in written:
        print(f"captura guardada: {path.relative_to(ROOT)}")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
