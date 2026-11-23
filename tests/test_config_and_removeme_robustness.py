# -*- coding: utf-8 -*-
"""Regresiones de configuración del editor y del removedor generado.

Cubre con código real:

- la preferencia de editor vive en ``config/settings.json`` de la raíz (o junto
  al ejecutable congelado), no dentro de ``lib/config``;
- un ``settings.json`` que no sea objeto no rompe ``Abrir con``;
- el removedor generado sobrevive a un ``install.json`` corrupto y sigue
  desinstalando;
- la vista previa del instalador ``.mexf`` tolera metadatos ilegibles.
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_default_editor_config_lives_at_app_root():
    import lib.editorDetector as editor_detector

    assert editor_detector._config_file_path() == ROOT / "config" / "settings.json"


def test_default_editor_config_follows_frozen_executable(tmp_path):
    import lib.editorDetector as editor_detector

    executable = tmp_path / "packagemaker"
    with patch.object(editor_detector.sys, "frozen", True, create=True), patch.object(
        editor_detector.sys, "executable", str(executable)
    ):
        assert editor_detector._config_file_path() == tmp_path / "config" / "settings.json"


@pytest.mark.parametrize("payload", ["[]", '"texto"', "5", "null", "true"])
def test_get_default_editor_tolerates_non_object(tmp_path, payload):
    import lib.editorDetector as editor_detector

    config = tmp_path / "settings.json"
    config.write_text(payload, encoding="utf-8")
    with patch.object(editor_detector, "_config_file_path", return_value=config):
        assert editor_detector.get_default_editor() is None


def test_save_default_editor_rewrites_non_object_and_roundtrips(tmp_path):
    import lib.editorDetector as editor_detector

    config = tmp_path / "settings.json"
    config.write_text("[]", encoding="utf-8")
    with patch.object(editor_detector, "_config_file_path", return_value=config):
        editor_detector.save_default_editor("code")
        assert editor_detector.get_default_editor() == "code"
    assert json.loads(config.read_text(encoding="utf-8")) == {"default_editor": "code"}


def test_save_default_editor_preserves_existing_keys(tmp_path):
    import lib.editorDetector as editor_detector

    config = tmp_path / "settings.json"
    config.write_text(json.dumps({"BASE_DIR": "/tmp/proyectos"}), encoding="utf-8")
    with patch.object(editor_detector, "_config_file_path", return_value=config):
        editor_detector.save_default_editor("cursor")
    data = json.loads(config.read_text(encoding="utf-8"))
    assert data == {"BASE_DIR": "/tmp/proyectos", "default_editor": "cursor"}


def _render_removeme(target: Path) -> Path:
    from lib.blindcubeEngine.asksome_installer import RECORD_NAME, _REMOVEME_TEMPLATE

    target.mkdir(parents=True, exist_ok=True)
    script = target / "removeme.py"
    script.write_text(
        _REMOVEME_TEMPLATE.format(
            app_id="demo", name="Demo", shortcuts=[], record_name=RECORD_NAME
        ),
        encoding="utf-8",
    )
    return script


@pytest.mark.parametrize(
    "payload", ["[]", '"texto"', "5", '{"shortcuts": 5}', '{"shortcuts": "x"}', "no-json"]
)
def test_generated_removeme_survives_corrupt_record(tmp_path, payload):
    from lib.blindcubeEngine.asksome_installer import RECORD_NAME

    target = tmp_path / "demo"
    script = _render_removeme(target)
    (target / RECORD_NAME).write_text(payload, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(script), "--silent"], capture_output=True, text=True
    )

    assert result.returncode == 0, result.stderr
    assert not target.exists()


def test_generated_removeme_still_deletes_recorded_shortcut(tmp_path):
    from lib.blindcubeEngine.asksome_installer import RECORD_NAME

    target = tmp_path / "demo"
    script = _render_removeme(target)
    shortcut = tmp_path / "demo.desktop"
    shortcut.write_text("[Desktop Entry]\n", encoding="utf-8")
    (target / RECORD_NAME).write_text(
        json.dumps({"shortcuts": [str(shortcut)]}), encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(script), "--silent"], capture_output=True, text=True
    )

    assert result.returncode == 0, result.stderr
    assert not shortcut.exists()
    assert not target.exists()


@pytest.mark.parametrize("payload", ["no-json", "[]", '"texto"', "5"])
def test_mexf_preview_metadata_tolerates_unreadable_input(tmp_path, payload):
    import packagemaker

    document = tmp_path / "malo.mexf"
    document.write_text(payload, encoding="utf-8")

    assert packagemaker._mexf_preview_metadata(document) is None
    assert packagemaker._mexf_preview_metadata(tmp_path / "missing.mexf") is None


def test_mexf_preview_metadata_reads_fields(tmp_path):
    import packagemaker

    document = tmp_path / "bueno.mexf"
    document.write_text(
        json.dumps({"name": "Demo", "version": "1.0", "description": "detalle"}),
        encoding="utf-8",
    )

    assert packagemaker._mexf_preview_metadata(document) == {
        "name": "Demo",
        "version": "1.0",
        "description": "detalle",
    }
