# -*- coding: utf-8 -*-
"""Instancia única de la aplicación (issue #25 / R-3d6a8f25)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from lib import single_instance

ROOT = Path(__file__).resolve().parents[1]

HOLDER = """
import os, sys, time
sys.path.insert(0, os.environ["ROOT"])
from lib.single_instance import claim
lock = claim()
print("ACQUIRED=", lock.acquired, flush=True)
print("PID=", os.getpid(), flush=True)
time.sleep(300)
"""


@pytest.fixture(autouse=True)
def _guard_enabled(tmp_path, monkeypatch):
    """Activa la guarda y aísla su cerrojo en una carpeta temporal."""
    monkeypatch.setenv(single_instance.DISABLE_ENV, "1")
    monkeypatch.setenv(single_instance.DIR_ENV, str(tmp_path))
    yield tmp_path


def _env(tmp_path):
    return dict(
        os.environ,
        PM_SINGLE_INSTANCE="1",
        PM_SINGLE_INSTANCE_DIR=str(tmp_path),
        ROOT=str(ROOT),
        PYTHONPATH=str(ROOT),
    )


@pytest.fixture
def holder(tmp_path):
    """Proceso aparte que retiene el cerrojo de verdad."""
    child = subprocess.Popen(
        [sys.executable, "-u", "-c", HOLDER],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=_env(tmp_path),
        cwd=str(ROOT),
    )
    acquired = child.stdout.readline().strip()
    pid_line = child.stdout.readline().strip()
    if acquired != "ACQUIRED= True" or not pid_line.startswith("PID= "):
        child.kill()
        child.wait()
        raise AssertionError(f"el proceso auxiliar no tomó el cerrojo: {acquired!r} {child.stderr.read()[-2000:]}")
    yield child
    child.kill()
    child.wait()


def test_claim_writes_the_owner_pid():
    lock = single_instance.claim()
    try:
        assert lock.acquired is True
        assert lock.holds_file is True
        assert single_instance.read_pid(lock.path) == os.getpid()
    finally:
        lock.release()
    assert not lock.path.exists()


def test_a_live_instance_blocks_the_second_claim(holder):
    second = single_instance.claim()
    assert second.acquired is False
    assert second.owner_pid == holder.pid
    assert second.holds_file is False
    assert second.fd is None


def test_the_lock_is_released_when_the_owner_dies(holder):
    assert single_instance.claim().acquired is False
    holder.kill()
    holder.wait()

    # El kernel suelta el bloqueo al morir el dueño: nada de cerrojos huérfanos.
    lock = single_instance.claim()
    try:
        assert lock.acquired is True
        assert single_instance.read_pid(lock.path) == os.getpid()
    finally:
        lock.release()


def test_a_leftover_file_does_not_block(tmp_path):
    path = tmp_path / "leftover.lock"
    path.write_text("\n999999", encoding="utf-8")

    lock = single_instance.claim(path)
    try:
        assert lock.acquired is True
    finally:
        lock.release()


def test_a_corrupt_lock_does_not_block(tmp_path):
    path = tmp_path / "corrupt.lock"
    path.write_text("no-es-un-pid\n", encoding="utf-8")

    lock = single_instance.claim(path)
    try:
        assert lock.acquired is True
    finally:
        lock.release()


def test_the_same_process_does_not_block_itself():
    first = single_instance.claim()
    try:
        again = single_instance.claim()
        assert again.acquired is True
        assert again is first
        assert again.holds_file is True
    finally:
        first.release()


def test_release_lets_a_new_instance_in(tmp_path, holder):
    holder.kill()
    holder.wait()
    first = single_instance.claim()
    first.release()

    second = single_instance.claim()
    try:
        assert second.acquired is True
    finally:
        second.release()


def test_the_switch_disables_the_guard(tmp_path, monkeypatch):
    monkeypatch.setenv(single_instance.DISABLE_ENV, "0")
    lock = single_instance.claim()
    assert lock.acquired is True
    assert lock.holds_file is False
    assert lock.fd is None
    assert not lock.path.exists()


def test_lock_path_is_per_user_and_honours_the_folder(tmp_path, monkeypatch):
    monkeypatch.setenv(single_instance.DIR_ENV, str(tmp_path))
    path = single_instance.lock_path()
    assert path.parent == tmp_path
    assert path.name.endswith(".lock")


def test_the_message_names_the_running_pid():
    message = single_instance.already_running_message(4321)
    assert "4321" in message
    assert single_instance.APP_NAME in message


PROBE = """
import os, sys
sys.path.insert(0, os.environ["ROOT"])
import packagemaker as pm

class ExplodingGUI:
    def __init__(self, *args, **kwargs):
        raise AssertionError("no debe construirse la ventana con otra instancia viva")

pm.PackageTodoGUI = ExplodingGUI
try:
    pm.main()
except SystemExit as exc:
    print("EXIT=", exc.code)
"""


def test_main_refuses_a_second_instance(tmp_path, holder):
    """Arranque real: con otra instancia viva, main() avisa y no abre ventana."""
    result = subprocess.run(
        [sys.executable, "-u", "-c", PROBE],
        capture_output=True,
        text=True,
        timeout=300,
        env=_env(tmp_path),
        cwd=str(ROOT),
    )
    assert result.returncode == 0, result.stderr[-3000:]
    assert f"EXIT= {single_instance.EXIT_ALREADY_RUNNING}" in result.stdout
    assert f"PID {holder.pid}" in result.stderr
    assert "ya está en ejecución" in result.stderr
    assert "no debe construirse la ventana" not in result.stderr
