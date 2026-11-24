# -*- coding: utf-8 -*-
"""Rutas de configuración ilegibles no deben tumbar el arranque ni el build.

En Python 3.13 ``Path.is_file()`` propaga ``PermissionError`` cuando el
directorio padre no es accesible. Tres rutas de configuración quedaban sin
protección:

* ``data/session.cache`` (``session_cache.load_session``) — se consulta en el
  arranque al restaurar la sesión de GitHub;
* ``config/settings.json`` del proyecto (``FlangCompiler``) — se consulta al
  construir el compilador desde el CLI o la QThread;
* ``config/settings.json`` de la aplicación (``editorDetector``) — se consulta
  al abrir o guardar la preferencia de «Abrir con».
"""
import os
from pathlib import Path
from unittest.mock import patch

import pytest

_UNREADABLE_SKIP = pytest.mark.skipif(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="los permisos POSIX no bloquean el acceso en Windows ni como root",
)


def _restore(path: Path, mode: int = 0o755) -> None:
    try:
        path.chmod(mode)
    except OSError:
        pass


@_UNREADABLE_SKIP
def test_session_cache_ignores_unreadable_data_dir(tmp_path):
    from lib import session_cache

    data = tmp_path / "data"
    data.mkdir()
    (data / "session.cache").write_bytes(b"not-a-real-cache")
    data.chmod(0o000)
    try:
        with patch.object(session_cache, "_data_dir", return_value=data):
            assert session_cache.load_session() is None
    finally:
        _restore(data)


@_UNREADABLE_SKIP
def test_flang_compiler_reports_unreadable_project_config(tmp_path):
    from lib.blindcubeEngine.BuildThread import FlangCompiler

    project = tmp_path / "project"
    config = project / "config"
    config.mkdir(parents=True)
    (project / "details.xml").write_text(
        "<package><app>demo</app></package>", encoding="utf-8"
    )
    (config / "settings.json").write_text("{}", encoding="utf-8")
    config.chmod(0o000)
    try:
        compiler = FlangCompiler(
            project, tmp_path / "out", log_callback=lambda _msg: None, sandbox=False
        )
        assert compiler.scripts_to_compile == []
        assert "config/settings.json" in compiler.last_error
    finally:
        _restore(config)


@_UNREADABLE_SKIP
def test_editor_detector_ignores_unreadable_config_dir(tmp_path):
    from lib import editorDetector

    config = tmp_path / "config"
    config.mkdir()
    settings = config / "settings.json"
    settings.write_text('{"default_editor": "code"}', encoding="utf-8")
    config.chmod(0o000)
    try:
        with patch.object(editorDetector, "_config_file_path", return_value=settings):
            assert editorDetector.get_default_editor() is None
            editorDetector.save_default_editor("vim")
    finally:
        _restore(config)
