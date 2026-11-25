# -*- coding: utf-8 -*-
"""Los iconos SVG no abortan la ventana con una instalación de solo lectura.

``IconManager`` creaba ``assets/icons`` en el constructor. En una instalación
sin permiso de escritura (``Program Files``) el ``mkdir`` lanzaba
``PermissionError`` y la tarjeta que pedía el icono no llegaba a construirse.
"""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("PyQt6.QtWidgets")

from lib.iconManager import IconManager  # noqa: E402

pytestmark = pytest.mark.skipif(
    not hasattr(os, "geteuid") or os.geteuid() == 0,
    reason="chmod no restringe la escritura al usuario root",
)


@pytest.fixture
def readonly_base(tmp_path):
    base = tmp_path / "instalacion"
    base.mkdir()
    os.chmod(base, 0o500)
    yield base
    os.chmod(base, 0o700)


def test_manager_is_created_without_write_permission(readonly_base):
    manager = IconManager(str(readonly_base))
    assert manager.icons_dir == readonly_base / "assets" / "icons"
    assert not manager.icons_dir.exists()


def test_missing_icon_falls_back_to_the_default_drawing(readonly_base):
    manager = IconManager(str(readonly_base))
    pixmap = manager.load_svg("app", 16)
    assert pixmap is not None and not pixmap.isNull()


def test_icon_path_is_none_instead_of_raising(readonly_base):
    manager = IconManager(str(readonly_base))
    assert manager.get_icon_path("app") is None


def test_svg_renderer_is_imported_from_the_right_module():
    from lib import iconManager

    assert iconManager.PYQT6_AVAILABLE, "QSvgRenderer no se pudo importar"


def test_existing_svg_is_rendered(tmp_path):
    icons = tmp_path / "app" / "assets" / "icons"
    icons.mkdir(parents=True)
    svg = icons / "app.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        '<rect width="24" height="24" fill="#ffffff"/></svg>',
        encoding="utf-8",
    )

    manager = IconManager(str(tmp_path / "app"))
    assert manager.get_icon_path("app") == str(svg)
    pixmap = manager.load_svg("app", 24)
    assert pixmap is not None and not pixmap.isNull()
