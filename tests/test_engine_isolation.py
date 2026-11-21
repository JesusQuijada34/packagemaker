# -*- coding: utf-8 -*-
"""Regresiones del aislamiento de motores y del manejo de bloqueos (Fase 1.2)."""

import errno
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_busy_errnos_are_detected_as_locks():
    from lib.file_ops import is_file_lock_error

    for code in (errno.EBUSY, errno.ETXTBSY, errno.EACCES, errno.EPERM):
        assert is_file_lock_error(OSError(code, "busy")), code


def test_missing_file_is_not_a_lock():
    from lib.file_ops import is_file_lock_error

    assert not is_file_lock_error(FileNotFoundError(errno.ENOENT, "nope"))


def test_winerror_32_is_detected(monkeypatch):
    from lib.file_ops import is_file_lock_error

    error = OSError(errno.EACCES, "sharing violation")
    error.winerror = 32
    assert is_file_lock_error(error)


def test_non_oserror_is_not_a_lock():
    from lib.file_ops import is_file_lock_error

    assert not is_file_lock_error(ValueError("nope"))


def test_remove_tree_deletes_nested_content(tmp_path):
    from lib.file_ops import remove_tree

    target = tmp_path / "build"
    (target / "nested").mkdir(parents=True)
    (target / "nested" / "binary.bin").write_bytes(b"x")
    assert remove_tree(target) is True
    assert not target.exists()


def test_remove_tree_on_missing_path_is_a_noop(tmp_path):
    from lib.file_ops import remove_tree

    assert remove_tree(tmp_path / "absent") is True


def test_remove_tree_retries_while_the_file_is_locked(tmp_path, monkeypatch):
    """Simula ``WinError 32`` en las dos primeras pasadas y luego libera."""
    import lib.file_ops as file_ops

    target = tmp_path / "locked"
    target.mkdir()
    (target / "a.bin").write_bytes(b"x")

    real_rmtree = file_ops.shutil.rmtree
    calls = {"n": 0}

    def flaky(path, **kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            error = OSError(errno.EACCES, "sharing violation")
            error.winerror = 32
            raise error
        return real_rmtree(path, **kwargs)

    monkeypatch.setattr(file_ops.shutil, "rmtree", flaky)
    monkeypatch.setattr(file_ops.time, "sleep", lambda _s: None)

    assert file_ops.remove_tree(target) is True
    assert calls["n"] == 3
    assert not target.exists()


def test_remove_tree_gives_up_without_raising(tmp_path, monkeypatch):
    import lib.file_ops as file_ops

    target = tmp_path / "stuck"
    target.mkdir()

    def always_locked(path, **kwargs):
        error = OSError(errno.EACCES, "sharing violation")
        error.winerror = 32
        raise error

    monkeypatch.setattr(file_ops.shutil, "rmtree", always_locked)
    monkeypatch.setattr(file_ops.time, "sleep", lambda _s: None)

    assert file_ops.remove_tree(target, attempts=3) is False


def test_copy_file_creates_parent_and_preserves_content(tmp_path):
    from lib.file_ops import copy_file

    source = tmp_path / "bin"
    source.write_bytes(b"payload")
    destination = copy_file(source, tmp_path / "out" / "deeper" / "bin")
    assert destination.read_bytes() == b"payload"


def test_copy_file_retries_on_lock(tmp_path, monkeypatch):
    import lib.file_ops as file_ops

    source = tmp_path / "src"
    source.write_bytes(b"payload")
    destination = tmp_path / "dst"

    real_copy2 = file_ops.shutil.copy2
    calls = {"n": 0}

    def flaky(src, dst, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            error = OSError(errno.EACCES, "sharing violation")
            error.winerror = 32
            raise error
        return real_copy2(src, dst, **kwargs)

    monkeypatch.setattr(file_ops.shutil, "copy2", flaky)
    monkeypatch.setattr(file_ops.time, "sleep", lambda _s: None)

    assert file_ops.copy_file(source, destination).read_bytes() == b"payload"
    assert calls["n"] == 2


def test_move_path_moves_between_directories(tmp_path):
    from lib.file_ops import move_path

    source = tmp_path / "a.txt"
    source.write_text("hello", encoding="utf-8")
    destination = move_path(source, tmp_path / "sub" / "b.txt")
    assert destination.read_text(encoding="utf-8") == "hello"
    assert not source.exists()


def test_replace_file_overwrites_destination(tmp_path):
    from lib.file_ops import replace_file

    source = tmp_path / "new.txt"
    source.write_text("new", encoding="utf-8")
    destination = tmp_path / "old.txt"
    destination.write_text("old", encoding="utf-8")
    replace_file(source, destination)
    assert destination.read_text(encoding="utf-8") == "new"


def test_blindcube_is_pinned_to_nuitka():
    from lib.engine_isolation import plan_engine

    plan = plan_engine("blindcube", Path("/tmp/work"))
    assert plan.backend == "nuitka"


def test_flatcube_is_pinned_to_pyinstaller():
    from lib.engine_isolation import plan_engine

    plan = plan_engine("flatcube", Path("/tmp/work"))
    assert plan.backend == "pyinstaller"


def test_blindcube_uses_lib_requirements():
    from lib.engine_isolation import plan_engine

    plan = plan_engine("blindcube", Path("/tmp/work"))
    assert plan.packages
    assert any(pkg.lower().startswith("nuitka") for pkg in plan.packages)


def test_flatcube_prefers_project_requirements(tmp_path):
    from lib.engine_isolation import plan_engine

    project = tmp_path / "proj"
    project.mkdir()
    (project / "requirements.txt").write_text("requests\n# comment\n", encoding="utf-8")
    plan = plan_engine("flatcube", tmp_path / "work", project)
    assert plan.packages == ["requests"]


def test_flatcube_falls_back_to_lib_requirements(tmp_path):
    from lib.engine_isolation import plan_engine

    plan = plan_engine("flatcube", tmp_path / "work", tmp_path / "empty")
    assert plan.packages


def test_each_engine_gets_its_own_venv(tmp_path):
    from lib.engine_isolation import plan_engine

    blind = plan_engine("blindcube", tmp_path)
    flat = plan_engine("flatcube", tmp_path)
    assert blind.venv_dir != flat.venv_dir
    assert blind.venv_dir.name == "venv-blindcube"
    assert flat.venv_dir.name == "venv-flatcube"


def test_unknown_engine_is_rejected(tmp_path):
    from lib.engine_core import EngineError
    from lib.engine_isolation import engine_environment

    with pytest.raises(EngineError):
        engine_environment("nope", tmp_path)


def test_engine_environment_carries_the_engine_requirements(tmp_path):
    from lib.engine_isolation import engine_environment

    env = engine_environment("blindcube", tmp_path)
    assert env.engine.id == "blindcube"
    assert env.requirements


def test_build_thread_never_falls_back_to_another_backend():
    """``_ensure_compiler`` ya no cae en silencio a PyInstaller."""
    source = (ROOT / "lib" / "BuildThread.py").read_text(encoding="utf-8")
    start = source.index("def _ensure_compiler")
    body = source[start : source.index("def parse_details_xml")]
    assert "backup" not in body.lower()
    assert "respaldo" not in body
    assert "no está disponible. " in body
