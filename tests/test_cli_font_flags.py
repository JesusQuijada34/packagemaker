"""Regresión: ``--force-fonts`` no debe caer en la TUI (R-6b1f8d20).

El flag estaba documentado como "forzar la redescarga aunque estén en caché",
pero solo se leía dentro de la rama de ``--download-fonts``. Usado solo, el CLI
no reconocía ninguna acción y arrancaba la interfaz de texto.
"""

from __future__ import annotations

import sys
from unittest.mock import patch

from lib.cliHandler import CLIHandler


def _resolve(argv):
    with patch.object(sys, "argv", ["packagemaker.py", *argv]):
        cli = CLIHandler(base_dir="/tmp/packagemaker-tests")
        args = cli.parse()
        return cli.get_action(args)


def test_force_fonts_alone_downloads_all_fonts():
    action, data, _options = _resolve(["--force-fonts"])
    assert action == "download_fonts"
    assert data == {"keys": "all", "force": True}


def test_download_fonts_alone_keeps_cache():
    action, data, _options = _resolve(["--download-fonts"])
    assert action == "download_fonts"
    assert data == {"keys": "all", "force": False}


def test_download_fonts_with_keys_and_force():
    action, data, _options = _resolve(["--download-fonts", "roboto,inter", "--force-fonts"])
    assert action == "download_fonts"
    assert data == {"keys": "roboto,inter", "force": True}
