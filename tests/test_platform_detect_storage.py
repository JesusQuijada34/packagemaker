# -*- coding: utf-8 -*-
"""Termux sin almacenamiento compartido sigue teniendo salida (R-6a2d8f43).

``compile_output_directory()`` comprobaba ``~/storage/downloads`` con
``Path.is_dir()``. En Termux sin ``termux-setup-storage`` ese directorio está
bajo un padre inaccesible y Python 3.13 propaga ``PermissionError``; el CLI
abortaba en lugar de usar ``/storage/emulated/0/Download``.
"""
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from lib import platform_detect

_UNREADABLE_SKIP = pytest.mark.skipif(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="los permisos POSIX no bloquean la lectura en Windows ni como root",
)


@_UNREADABLE_SKIP
def test_termux_falls_back_when_storage_is_unreadable(tmp_path):
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o000)
    try:
        target = str(locked / "storage" / "downloads")
        with patch.object(platform_detect.os.path, "expanduser", return_value=target):
            path = platform_detect.compile_output_directory("termux")
    finally:
        try:
            locked.chmod(0o755)
        except OSError:
            pass
    assert path == str(Path("/storage/emulated/0/Download"))


def test_termux_keeps_shared_download_when_available(tmp_path):
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    with patch.object(platform_detect.os.path, "expanduser", return_value=str(downloads)):
        assert platform_detect.compile_output_directory("termux") == str(downloads)
