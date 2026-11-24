import hashlib
import hmac
import io
import json
import lzma
import os
import tarfile
from pathlib import Path

import pytest

from lib.blindcubeEngine import asksome_format
from lib.blindcubeEngine.asksome_format import AsksomeError, extract_asksome, pack_asksome, verify_asksome
from lib.mexf_parser import (
    MexfDocument,
    MexfError,
    detect_mexf_format,
    migrate_legacy_mexf,
    parse_mexf,
)


def test_legacy_mexf_is_detected_and_migrated(tmp_path):
    source = tmp_path / "legacy.mexf"
    source.write_text(
        json.dumps(
            {
                "version": "1.0",
                "app_name": "Legacy App",
                "app_id": "com.example.legacy",
                "extensions": [{"extension": ".iflapp"}],
            }
        ),
        encoding="utf-8",
    )
    assert detect_mexf_format(source) == "legacy-json"
    target = tmp_path / "main.mexf"
    migrate_legacy_mexf(source, target)
    document = parse_mexf(target)
    assert document.source_format == "yaml-v1"
    assert document.metadata["id"] == "com.example.legacy"


def test_shipped_example_mexf_is_yaml(tmp_path):
    """El ``example.mexf`` del repositorio ya no es JSON legacy: es el shell YAML."""
    source = Path(__file__).resolve().parents[1] / "example.mexf"
    assert detect_mexf_format(source) == "yaml-v1"
    document = parse_mexf(source)
    assert document.metadata["id"] == "com.fluthin.packagemaker"
    assert document.data["file_associations"]


def test_invalid_mexf_reports_contract_error(tmp_path):
    path = tmp_path / "bad.mexf"
    path.write_text("format: mexf\nversion: 1\nmetadata: {}\n", encoding="utf-8")
    with pytest.raises(MexfError):
        parse_mexf(path)


def test_asksome_is_deterministic_and_round_trips(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "launcher.py").write_text("print('ok')\n", encoding="utf-8")
    first = pack_asksome(staging, tmp_path / "one.asksome", metadata={"id": "demo"})
    second = pack_asksome(staging, tmp_path / "two.asksome", metadata={"id": "demo"})
    assert first.read_bytes() == second.read_bytes()
    assert verify_asksome(first)["format"] == "asksome"
    target = tmp_path / "out"
    assert (target / "launcher.py") in extract_asksome(first, target)


def test_asksome_tampering_is_rejected(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "a.txt").write_text("a", encoding="utf-8")
    artifact = pack_asksome(staging, tmp_path / "x.asksome")
    data = bytearray(artifact.read_bytes())
    data[-1] ^= 1
    artifact.write_bytes(data)
    with pytest.raises(AsksomeError):
        verify_asksome(artifact)


def _tar_payload(names):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as tar:
        for name in names:
            data = b"x"
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return lzma.compress(stream.getvalue(), format=lzma.FORMAT_ALONE)


def _craft_asksome(path, *, names=(), payload=None, header=None):
    """Escribe un .asksome firmado con la clave local para probar el lector."""
    payload = payload if payload is not None else _tar_payload(names)
    data = {
        "format": "asksome",
        "format_version": 1,
        "manifest": [],
        "metadata": {},
        "compression": "lzma",
        "encryption": "none",
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
    }
    data.update(header or {})
    signature = hmac.new(
        asksome_format.KEY, asksome_format._canonical(data) + payload, hashlib.sha256
    ).hexdigest()
    data["signature"] = signature
    header_bytes = asksome_format._canonical(data)
    Path(path).write_bytes(
        asksome_format.MAGIC + len(header_bytes).to_bytes(4, "little") + header_bytes + payload
    )
    return Path(path)


def _write_raw_asksome(path, header_bytes, *, declared_size=None, payload=b""):
    size = len(header_bytes) if declared_size is None else declared_size
    Path(path).write_bytes(
        asksome_format.MAGIC + size.to_bytes(4, "little") + header_bytes + payload
    )
    return Path(path)


class TestAsksomeMalformedHeaderTests:
    def test_non_object_header_is_rejected(self, tmp_path):
        artifact = _write_raw_asksome(tmp_path / "list.asksome", b"[]")
        with pytest.raises(AsksomeError):
            asksome_format.read_asksome_header(artifact)
        with pytest.raises(AsksomeError):
            verify_asksome(artifact)
        with pytest.raises(AsksomeError):
            extract_asksome(artifact, tmp_path / "out")

    def test_truncated_header_is_rejected(self, tmp_path):
        artifact = _write_raw_asksome(
            tmp_path / "cut.asksome", b'{"format":"asksome"}', declared_size=9999
        )
        with pytest.raises(AsksomeError):
            asksome_format.read_asksome_header(artifact)

    @pytest.mark.parametrize(
        "override",
        [
            {"metadata": []},
            {"manifest": "x"},
            {"icon": 123},
            {"encryption_params": []},
            {"format_version": "1"},
        ],
    )
    def test_wrong_header_field_types_are_rejected(self, tmp_path, override):
        artifact = _craft_asksome(tmp_path / "bad.asksome", header=override)
        with pytest.raises(AsksomeError):
            verify_asksome(artifact)
        with pytest.raises(AsksomeError):
            extract_asksome(artifact, tmp_path / "out")

    @pytest.mark.parametrize(
        "name",
        ["C:/Windows/evil.txt", "C:evil.txt", "../evil.txt", "/tmp/evil.txt", ".."],
    )
    def test_unsafe_member_paths_are_rejected(self, tmp_path, name):
        artifact = _craft_asksome(tmp_path / "traversal.asksome", names=[name])
        target = tmp_path / "unpacked"
        with pytest.raises(AsksomeError):
            extract_asksome(artifact, target)
        assert not (tmp_path / "evil.txt").exists()
        assert not (target / "evil.txt").exists()

    def test_corrupt_payload_raises_asksome_error(self, tmp_path):
        artifact = _craft_asksome(tmp_path / "corrupt.asksome", payload=b"not lzma at all")
        with pytest.raises(AsksomeError):
            extract_asksome(artifact, tmp_path / "out")


DETAILS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<app>
  <publisher>Influent</publisher>
  <app>demo</app>
  <name>Demo App</name>
  <version>v1.0-25.01-10.00</version>
  <author>JesusQuijada34</author>
  <platform>AlphaCube</platform>
</app>
"""

MAIN_MEXF = """format: mexf
version: 1
metadata:
  id: influent.demo
  name: Demo App
  version: v1.0
runtime:
  launcher: argv
commands:
  - id: demo.hello
    executable: demo.exe
    args: ["--hello"]
"""

MODULE_MEXF = """format: mexf
version: 1
metadata:
  id: influent.demo.extra
  name: Demo Extra
  version: v1.0
triggers:
  - id: demo.trigger
"""


def _make_project(tmp_path):
    root = tmp_path / "proj"
    (root / ".mexf").mkdir(parents=True)
    (root / "details.xml").write_text(DETAILS_XML, encoding="utf-8")
    (root / ".mexf" / "main.mexf").write_text(MAIN_MEXF, encoding="utf-8")
    (root / ".mexf" / "extra.mexf").write_text(MODULE_MEXF, encoding="utf-8")
    (root / "logo.txt").write_text("logo", encoding="utf-8")
    return root


def test_compile_mexf_project_builds_signed_asksome(tmp_path):
    from lib.mexf_compiler import compile_mexf_project

    root = _make_project(tmp_path)
    result = compile_mexf_project(root, tmp_path / "out.asksome")
    assert result.output.is_file()
    header = verify_asksome(result.output)
    assert header["format"] == "asksome"
    assert header["metadata"]["id"] == "influent.demo"
    assert header["metadata"]["publisher"] == "Influent"
    assert set(header["metadata"]["modules"]) == {".mexf/main.mexf", ".mexf/extra.mexf"}
    staged = extract_asksome(result.output, tmp_path / "unpacked")
    names = {path.name for path in staged}
    assert {"main.mexf", "launcher.py", "details.xml"} <= names


def test_compile_mexf_project_merges_submodules(tmp_path):
    from lib.mexf_compiler import compile_mexf_project

    root = _make_project(tmp_path)
    result = compile_mexf_project(root, tmp_path / "out.asksome")
    assert result.modules == [".mexf/main.mexf", ".mexf/extra.mexf"]
    unpacked = tmp_path / "unpacked"
    extract_asksome(result.output, unpacked)
    merged = json.loads((unpacked / "main.mexf").read_text(encoding="utf-8"))
    assert [item["id"] for item in merged["commands"]] == ["demo.hello"]
    assert [item["id"] for item in merged["triggers"]] == ["demo.trigger"]


def test_compile_mexf_project_is_deterministic(tmp_path):
    from lib.mexf_compiler import compile_mexf_project

    root = _make_project(tmp_path)
    first = compile_mexf_project(root, tmp_path / "one.asksome").output
    second = compile_mexf_project(root, tmp_path / "two.asksome").output
    assert first.read_bytes() == second.read_bytes()


def test_compile_mexf_project_rejects_asset_traversal(tmp_path):
    from lib.mexf_compiler import MexfCompileError, compile_mexf_project

    root = _make_project(tmp_path)
    bad = MAIN_MEXF + "assets:\n  - path: ../escape.txt\n"
    (root / ".mexf" / "main.mexf").write_text(bad, encoding="utf-8")
    with pytest.raises(MexfCompileError):
        compile_mexf_project(root, tmp_path / "bad.asksome")


def test_compile_mexf_project_reports_unwritable_output_as_compile_error(tmp_path):
    """Un destino que es carpeta o no se puede escribir no debe lanzar OSError crudo."""
    from lib.mexf_compiler import MexfCompileError, compile_mexf_project

    root = _make_project(tmp_path)
    output_dir = tmp_path / "salida"
    output_dir.mkdir()

    with pytest.raises(MexfCompileError):
        compile_mexf_project(root, output_dir)

    blocker = tmp_path / "archivo"
    blocker.write_text("no soy un directorio", encoding="utf-8")
    with pytest.raises(MexfCompileError):
        compile_mexf_project(root, blocker / "demo.asksome")


_UNREADABLE_SKIP = pytest.mark.skipif(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="los permisos POSIX no bloquean la lectura en Windows ni como root",
)


@_UNREADABLE_SKIP
def test_parse_mexf_reports_unreadable_source_as_mexf_error(tmp_path):
    """Un .mexf sin permiso de lectura no debe escapar como OSError crudo."""
    source = tmp_path / "main.mexf"
    source.write_text(MAIN_MEXF, encoding="utf-8")
    source.chmod(0)
    try:
        assert detect_mexf_format(source) == "unknown"
        with pytest.raises(MexfError):
            parse_mexf(source)
    finally:
        source.chmod(0o644)


@_UNREADABLE_SKIP
def test_compile_mexf_project_reports_unreadable_module_as_compile_error(tmp_path):
    from lib.mexf_compiler import MexfCompileError, compile_mexf_project

    root = _make_project(tmp_path)
    module = root / ".mexf" / "main.mexf"
    module.chmod(0)
    try:
        with pytest.raises(MexfCompileError):
            compile_mexf_project(root, tmp_path / "out.asksome")
    finally:
        module.chmod(0o644)


@_UNREADABLE_SKIP
def test_compile_mexf_project_reports_unreadable_details_as_compile_error(tmp_path):
    from lib.mexf_compiler import MexfCompileError, compile_mexf_project

    root = _make_project(tmp_path)
    details = root / "details.xml"
    details.chmod(0)
    try:
        with pytest.raises(MexfCompileError):
            compile_mexf_project(root, tmp_path / "out.asksome")
    finally:
        details.chmod(0o644)


@_UNREADABLE_SKIP
def test_compile_mexf_project_reports_unreadable_module_directory(tmp_path):
    from lib.mexf_compiler import MexfCompileError, compile_mexf_project

    root = _make_project(tmp_path)
    mexf_dir = root / ".mexf"
    mexf_dir.chmod(0)
    try:
        with pytest.raises(MexfCompileError):
            compile_mexf_project(root, tmp_path / "out.asksome")
    finally:
        mexf_dir.chmod(0o755)


@_UNREADABLE_SKIP
def test_compile_mexf_helper_reports_unreadable_input_without_traceback(tmp_path, capsys):
    from lib.cliHandler import MexfCompileHelper

    root = _make_project(tmp_path)
    details = root / "details.xml"
    details.chmod(0)
    try:
        assert MexfCompileHelper.compile({"path": str(root)}) is False
    finally:
        details.chmod(0o644)
    assert "[ERROR] Compilación .mexf fallida:" in capsys.readouterr().out


def test_mexf_compiler_skips_projects_without_mexf_dir(tmp_path):
    from lib.mexf_compiler import MexfCompiler

    root = tmp_path / "plain"
    root.mkdir()
    assert MexfCompiler(root).run() is None


def test_buildthread_compiles_mexf_before_iflapp(tmp_path):
    from lib.blindcubeEngine.BuildThread import FlangCompiler

    root = _make_project(tmp_path)
    output = tmp_path / "releases"
    logs = []
    compiler = FlangCompiler(root, output, log_callback=logs.append, sandbox=False)
    artifact = compiler._compile_mexf_if_present()
    assert artifact is not None
    assert artifact.parent == output
    assert artifact.suffix == ".asksome"
    assert any("asksome" in step.lower() for step in compiler.procedure)
    assert any("Leer details.xml" in step for step in compiler.procedure)


def test_buildthread_skips_mexf_when_absent(tmp_path):
    from lib.blindcubeEngine.BuildThread import FlangCompiler

    root = tmp_path / "plain"
    root.mkdir()
    (root / "details.xml").write_text(DETAILS_XML, encoding="utf-8")
    compiler = FlangCompiler(root, tmp_path / "releases", log_callback=lambda _m: None, sandbox=False)
    assert compiler._compile_mexf_if_present() is None
    assert compiler.procedure == []


def _install_fixture(tmp_path):
    from lib.mexf_compiler import compile_mexf_project

    root = _make_project(tmp_path)
    artifact = compile_mexf_project(root, tmp_path / "demo.asksome").output
    install_root = tmp_path / "installed"
    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()
    return artifact, install_root, shortcuts


def test_install_asksome_extracts_and_records(tmp_path):
    from lib.blindcubeEngine.asksome_installer import install_asksome, list_installed, read_record

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    assert record.app_id == "influent.demo"
    assert Path(record.install_dir).is_dir()
    assert (Path(record.install_dir) / "launcher.py").is_file()
    assert (Path(record.install_dir) / "install.json").is_file()
    assert (Path(record.install_dir) / "removeme.py").is_file()
    assert record.shortcuts and Path(record.shortcuts[0]).is_file()
    assert [item.app_id for item in list_installed(install_root)] == ["influent.demo"]
    assert read_record("influent.demo", install_root).version == "v1.0"


def test_uninstall_asksome_purges_files_and_shortcuts(tmp_path):
    from lib.blindcubeEngine.asksome_installer import install_asksome, list_installed, uninstall_asksome

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    removed = uninstall_asksome(record.app_id, install_root)
    assert not Path(record.install_dir).exists()
    assert all(not Path(item).exists() for item in record.shortcuts)
    assert removed
    assert list_installed(install_root) == []


def test_uninstall_silent_on_missing(tmp_path):
    from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, uninstall_asksome

    assert uninstall_asksome("nope", tmp_path / "installed", silent=True) == []
    with pytest.raises(AsksomeInstallError):
        uninstall_asksome("nope", tmp_path / "installed")


@pytest.mark.parametrize("app_id", ["..", ".", "../victim", "/etc", "C:evil", "a/b", "a\\b"])
def test_uninstall_rejects_app_id_that_escapes_install_root(tmp_path, app_id):
    from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, uninstall_asksome

    install_root = tmp_path / "installed"
    install_root.mkdir()
    victim = tmp_path / "victim"
    victim.mkdir()
    (victim / "keep.txt").write_text("importante", encoding="utf-8")

    with pytest.raises(AsksomeInstallError):
        uninstall_asksome(app_id, install_root)

    assert (victim / "keep.txt").is_file()


@_UNREADABLE_SKIP
def test_install_asksome_skips_unwritable_shortcut_dir(tmp_path):
    """Una carpeta de accesos directos de sólo lectura no aborta la instalación."""
    from lib.blindcubeEngine.asksome_installer import install_asksome

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    shortcuts.chmod(0o555)
    try:
        record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    finally:
        shortcuts.chmod(0o755)

    assert record.shortcuts == []
    assert (Path(record.install_dir) / "install.json").is_file()


@_UNREADABLE_SKIP
def test_install_asksome_reports_unreadable_artifact(tmp_path):
    from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, install_asksome

    artifact, install_root, _shortcuts = _install_fixture(tmp_path)
    blocked = tmp_path / "privado"
    blocked.mkdir()
    moved = blocked / artifact.name
    artifact.replace(moved)
    blocked.chmod(0o000)
    try:
        with pytest.raises(AsksomeInstallError):
            install_asksome(moved, install_root, create_desktop_shortcuts=False)
    finally:
        blocked.chmod(0o755)


@_UNREADABLE_SKIP
def test_uninstall_asksome_reports_unreadable_root(tmp_path):
    from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, uninstall_asksome

    root = tmp_path / "installed"
    (root / "demo.app").mkdir(parents=True)
    root.chmod(0o000)
    try:
        with pytest.raises(AsksomeInstallError):
            uninstall_asksome("demo.app", root)
    finally:
        root.chmod(0o755)


@_UNREADABLE_SKIP
def test_uninstall_asksome_skips_blocked_shortcut(tmp_path):
    """Un acceso directo ilegible no impide purgar la instalación."""
    from lib.blindcubeEngine.asksome_installer import install_asksome, uninstall_asksome

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    assert record.shortcuts
    shortcuts.chmod(0o000)
    try:
        removed = uninstall_asksome(record.app_id, install_root)
    finally:
        shortcuts.chmod(0o755)

    assert not Path(record.install_dir).exists()
    assert str(Path(record.install_dir)) in removed


@_UNREADABLE_SKIP
def test_uninstall_asksome_reports_blocked_tree(tmp_path):
    """Si el árbol no se puede borrar, se informa con AsksomeInstallError."""
    from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, install_asksome, uninstall_asksome

    artifact, install_root, _shortcuts = _install_fixture(tmp_path)
    record = install_asksome(artifact, install_root, create_desktop_shortcuts=False)
    locked = Path(record.install_dir) / "locked"
    locked.mkdir()
    (locked / "f.txt").write_text("x", encoding="utf-8")
    locked.chmod(0o555)
    try:
        with pytest.raises(AsksomeInstallError):
            uninstall_asksome(record.app_id, install_root)
    finally:
        locked.chmod(0o755)


def test_read_record_and_build_removeme_reject_unsafe_app_id(tmp_path):
    from lib.blindcubeEngine.asksome_installer import (
        AsksomeInstallError,
        build_removeme,
        read_record,
    )

    install_root = tmp_path / "installed"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "install.json").write_text("{}", encoding="utf-8")

    with pytest.raises(AsksomeInstallError):
        read_record("../outside", install_root)
    with pytest.raises(AsksomeInstallError):
        build_removeme("../outside", install_root)


@_UNREADABLE_SKIP
def test_read_record_reports_unreadable_install_root(tmp_path):
    """``--build-removeme`` no debe lanzar ``PermissionError`` crudo (R-9e1a4c72)."""
    from lib.blindcubeEngine.asksome_installer import (
        AsksomeInstallError,
        build_removeme,
        read_record,
    )

    install_root = tmp_path / "installed"
    app_dir = install_root / "influent.demo"
    app_dir.mkdir(parents=True)
    (app_dir / "install.json").write_text("{}", encoding="utf-8")
    install_root.chmod(0o000)
    try:
        with pytest.raises(AsksomeInstallError) as read_error:
            read_record("influent.demo", install_root)
        assert "No se pudo acceder" in str(read_error.value)
        with pytest.raises(AsksomeInstallError):
            build_removeme("influent.demo", install_root)
    finally:
        install_root.chmod(0o755)


def test_install_reports_unusable_install_root(tmp_path):
    from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, install_asksome

    artifact, install_root, _shortcuts = _install_fixture(tmp_path)

    blocked_root = tmp_path / "blocked-root"
    blocked_root.write_text("no es un directorio", encoding="utf-8")
    with pytest.raises(AsksomeInstallError):
        install_asksome(artifact, blocked_root, create_desktop_shortcuts=False)

    install_root.mkdir()
    (install_root / "influent.demo").write_text("bloquea el destino", encoding="utf-8")
    with pytest.raises(AsksomeInstallError):
        install_asksome(artifact, install_root, create_desktop_shortcuts=False)


def test_install_rejects_dot_app_id_without_deleting_parent(tmp_path):
    """Un ``.asksome`` con id ``..`` no puede borrar el padre de la raíz."""
    from lib.blindcubeEngine.asksome_installer import install_asksome

    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "launcher.py").write_text("print('hola')\n", encoding="utf-8")
    artifact = tmp_path / "evil.asksome"
    pack_asksome(
        payload,
        artifact,
        metadata={"id": "..", "name": "Evil", "version": "1.0"},
        launcher="launcher.py",
    )

    install_root = tmp_path / "installed"
    install_root.mkdir()
    marker = tmp_path / "marker.txt"
    marker.write_text("no borrar", encoding="utf-8")

    record = install_asksome(artifact, install_root, create_desktop_shortcuts=False)

    assert marker.is_file()
    assert Path(record.install_dir) == (install_root / "asksome.app").resolve()
    assert Path(record.install_dir).is_dir()


def test_generated_removeme_runs_silently(tmp_path):
    import subprocess
    import sys as _sys

    from lib.blindcubeEngine.asksome_installer import install_asksome

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    script = Path(record.install_dir) / "removeme.py"
    result = subprocess.run(
        [_sys.executable, str(script), "--silent"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0
    assert not Path(record.install_dir).exists()


def test_install_rejects_tampered_artifact(tmp_path):
    from lib.blindcubeEngine.asksome_format import AsksomeError
    from lib.blindcubeEngine.asksome_installer import install_asksome

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    data = bytearray(artifact.read_bytes())
    data[-1] ^= 1
    artifact.write_bytes(data)
    with pytest.raises(AsksomeError):
        install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])


VALID_SOURCE = """format: mexf
version: 1
metadata:
  id: influent.editor-demo
  name: Editor Demo
  version: v1.0
runtime:
  launcher: argv
commands: []
"""


def test_lint_accepts_valid_source():
    from lib.mexf_editor import is_valid_source, lint_source

    assert lint_source(VALID_SOURCE) == []
    assert is_valid_source(VALID_SOURCE)


def test_lint_reports_yaml_error_with_line():
    from lib.mexf_editor import lint_source

    broken = "format: mexf\nmetadata:\n  id: [unclosed\n"
    issues = lint_source(broken)
    assert issues
    assert issues[0].line >= 1
    assert issues[0].severity == "error"


def test_lint_reports_contract_violation_with_line():
    from lib.mexf_editor import lint_source

    bad = "format: mexf\nversion: 1\nmetadata:\n  name: Sin Id\n"
    issues = lint_source(bad)
    assert any("id" in issue.message.lower() for issue in issues)
    assert all(issue.line >= 1 for issue in issues)


def test_compile_source_builds_asksome(tmp_path):
    from lib.blindcubeEngine.asksome_format import verify_asksome
    from lib.mexf_editor import compile_source

    output = compile_source(VALID_SOURCE, tmp_path / "editor.asksome")
    assert output.is_file()
    header = verify_asksome(output)
    assert header["metadata"]["id"] == "influent.editor-demo"


def test_compile_source_rejects_invalid_text(tmp_path):
    from lib.mexf_editor import compile_source
    from lib.mexf_parser import MexfError

    with pytest.raises(MexfError):
        compile_source("format: mexf\nmetadata: {}\n", tmp_path / "bad.asksome")


def test_encrypted_asksome_round_trips_with_password(tmp_path):
    from lib.mexf_compiler import compile_mexf_project

    root = _make_project(tmp_path)
    result = compile_mexf_project(root, tmp_path / "enc.asksome", password="s3cret")
    header = verify_asksome(result.output)
    assert header["encryption"] != "none"
    # El payload cifrado no filtra texto en claro.
    assert b"demo.hello" not in result.output.read_bytes()
    staged = extract_asksome(result.output, tmp_path / "unpacked", password="s3cret")
    assert {path.name for path in staged} >= {"main.mexf", "launcher.py"}


def test_encrypted_asksome_requires_correct_password(tmp_path):
    from lib.blindcubeEngine.iflapp_format import IflappSignatureError
    from lib.mexf_compiler import compile_mexf_project

    root = _make_project(tmp_path)
    result = compile_mexf_project(root, tmp_path / "enc.asksome", password="s3cret")
    with pytest.raises(IflappSignatureError):
        extract_asksome(result.output, tmp_path / "nope", password="wrong")


def test_encrypted_asksome_needs_password(tmp_path):
    from lib.blindcubeEngine.iflapp_format import IflappError
    from lib.mexf_compiler import compile_mexf_project

    root = _make_project(tmp_path)
    result = compile_mexf_project(root, tmp_path / "enc.asksome", password="s3cret")
    with pytest.raises(IflappError):
        extract_asksome(result.output, tmp_path / "nope")


def test_wrappers_are_generated_and_valid_python(tmp_path):
    from lib.mexf_compiler import compile_mexf_project

    root = _make_project(tmp_path)
    result = compile_mexf_project(root, tmp_path / "out.asksome", wrappers=True)
    names = {wrapper.name for wrapper in result.wrappers}
    assert names == {"out.check-syntax.py", "out.check-env.py"}
    for wrapper in result.wrappers:
        assert wrapper.is_file()
        compile(wrapper.read_text(encoding="utf-8"), str(wrapper), "exec")


def test_syntax_wrapper_runs_against_valid_artifact(tmp_path):
    import subprocess
    import sys

    from lib.mexf_compiler import compile_mexf_project

    root = _make_project(tmp_path)
    result = compile_mexf_project(root, tmp_path / "out.asksome", wrappers=True)
    wrapper = next(w for w in result.wrappers if w.name.endswith("check-syntax.py"))
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    proc = subprocess.run([sys.executable, str(wrapper)], capture_output=True, text=True, env=env)
    assert proc.returncode == 0, proc.stderr
    assert "[syntax] OK" in proc.stdout


def test_generated_removeme_is_autonomous_and_self_contained(tmp_path):
    """El script no debe depender del repositorio de PackageMaker."""
    from lib.blindcubeEngine.asksome_installer import install_asksome

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    body = (Path(record.install_dir) / "removeme.py").read_text(encoding="utf-8")
    assert "sys.path.insert" not in body
    assert "from lib." not in body
    assert record.remover == "removeme.py"


def test_removeme_binary_name_matches_platform():
    import sys as _sys

    from lib.blindcubeEngine.asksome_installer import removeme_binary_name

    name = removeme_binary_name()
    if _sys.platform.startswith("win"):
        assert name == "removeme.exe"
    elif _sys.platform == "darwin":
        assert name == "removeme.app"
    else:
        assert name == "removeme.elf"


def test_install_compiles_removeme_binary(tmp_path):
    """Con ``removeme_binary=True`` se escribe el binario nativo y se registra."""
    from lib.blindcubeEngine.asksome_installer import install_asksome, removeme_binary_name

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(
        artifact, install_root, shortcut_dirs=[shortcuts], removeme_binary=True
    )
    binary = Path(record.install_dir) / removeme_binary_name()
    assert binary.is_file()
    assert os.access(binary, os.X_OK)
    assert record.remover == removeme_binary_name()
    assert json.loads((Path(record.install_dir) / "install.json").read_text())["remover"] == record.remover


def test_compiled_removeme_binary_purges_installation(tmp_path):
    import subprocess

    from lib.blindcubeEngine.asksome_installer import install_asksome, list_installed

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(
        artifact, install_root, shortcut_dirs=[shortcuts], removeme_binary=True
    )
    binary = Path(record.install_dir) / record.remover
    assert binary.is_file()
    result = subprocess.run([str(binary), "--silent"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert not Path(record.install_dir).exists()
    assert all(not Path(item).exists() for item in record.shortcuts)
    assert list_installed(install_root) == []


def test_build_removeme_for_existing_installation(tmp_path):
    from lib.blindcubeEngine.asksome_installer import build_removeme, install_asksome, removeme_binary_name

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    assert record.remover == "removeme.py"
    binary = build_removeme(record.app_id, install_root)
    assert binary is not None and binary.name == removeme_binary_name()
    assert binary.is_file()


def test_removeme_has_gui_with_console_fallback(tmp_path):
    """La plantilla trae GUI (PyQt6) con respaldo a consola, sin importar ``lib``."""
    from lib.blindcubeEngine.asksome_installer import install_asksome

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    body = (Path(record.install_dir) / "removeme.py").read_text(encoding="utf-8")
    assert "_GuiReporter" in body and "_ConsoleReporter" in body
    assert "QProgressDialog" in body
    assert "from lib" not in body


def test_generated_removeme_console_mode_reports_removals(tmp_path):
    import subprocess
    import sys as _sys

    from lib.blindcubeEngine.asksome_installer import install_asksome

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    script = Path(record.install_dir) / "removeme.py"
    result = subprocess.run(
        [_sys.executable, str(script), "--console"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "eliminado:" in result.stdout
    assert not Path(record.install_dir).exists()


# --- Accesos directos .desktop y registros de instalación -------------------


def _record_with(install_dir: Path, **overrides) -> "object":
    from lib.blindcubeEngine.asksome_installer import InstallRecord

    data = dict(
        app_id="influent.demo",
        name="Demo",
        version="v1.0-26.11-10.00",
        install_dir=str(install_dir),
        artifact="demo.asksome",
        artifact_sha256="0" * 64,
        launcher="launcher.py",
    )
    data.update(overrides)
    return InstallRecord(**data)


def test_linux_desktop_quotes_exec_arguments_with_spaces(tmp_path):
    from lib.blindcubeEngine.asksome_installer import _write_linux_desktop

    install_dir = tmp_path / "My Apps" / "influent.demo"
    install_dir.mkdir(parents=True)
    entry = _write_linux_desktop(tmp_path / "shortcuts", _record_with(install_dir))
    exec_line = next(
        line for line in entry.read_text(encoding="utf-8").splitlines() if line.startswith("Exec=")
    )
    # Dos argumentos citados: intérprete y lanzador.
    assert exec_line.count('"') == 4
    assert f'"{install_dir / "launcher.py"}"' in exec_line


def test_linux_desktop_name_cannot_inject_new_keys(tmp_path):
    from lib.blindcubeEngine.asksome_installer import _write_linux_desktop

    install_dir = tmp_path / "influent.demo"
    install_dir.mkdir()
    record = _record_with(install_dir, name="Demo\nTerminal=true\nExec=/bin/sh")
    body = _write_linux_desktop(tmp_path / "shortcuts", record).read_text(encoding="utf-8")
    assert "\nTerminal=true" not in body
    assert body.count("\nExec=") == 1
    assert "Name=Demo Terminal=true Exec=/bin/sh" in body


def test_desktop_exec_quote_escapes_field_codes():
    from lib.linux_icon_handler import _desktop_exec_quote

    assert _desktop_exec_quote("/tmp/100%/app") == '"/tmp/100%%/app"'


def test_read_record_rejects_corrupt_and_incomplete(tmp_path):
    from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, read_record

    app_dir = tmp_path / "influent.demo"
    app_dir.mkdir()

    (app_dir / "install.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(AsksomeInstallError):
        read_record("influent.demo", tmp_path)

    (app_dir / "install.json").write_text("[]", encoding="utf-8")
    with pytest.raises(AsksomeInstallError):
        read_record("influent.demo", tmp_path)

    (app_dir / "install.json").write_text(json.dumps({"app_id": "influent.demo"}), encoding="utf-8")
    with pytest.raises(AsksomeInstallError):
        read_record("influent.demo", tmp_path)


def test_build_removeme_reports_corrupt_record(tmp_path):
    from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, build_removeme

    app_dir = tmp_path / "installed" / "influent.demo"
    app_dir.mkdir(parents=True)
    (app_dir / "install.json").write_text("{bad", encoding="utf-8")
    with pytest.raises(AsksomeInstallError):
        build_removeme("influent.demo", tmp_path / "installed")


def test_read_record_rejects_non_text_required_fields(tmp_path):
    from lib.blindcubeEngine.asksome_installer import AsksomeInstallError, read_record

    app_dir = tmp_path / "influent.demo"
    app_dir.mkdir()
    data = {
        "app_id": 5,
        "name": "Demo",
        "version": "v1.0",
        "install_dir": str(app_dir),
        "artifact": "demo.asksome",
        "artifact_sha256": "0" * 64,
        "launcher": "launcher.py",
    }
    (app_dir / "install.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(AsksomeInstallError):
        read_record("influent.demo", tmp_path)


def test_uninstall_tolerates_wrong_field_types_in_record(tmp_path):
    from lib.blindcubeEngine.asksome_installer import read_record, uninstall_asksome

    install_root = tmp_path / "installed"
    app_dir = install_root / "influent.demo"
    app_dir.mkdir(parents=True)
    (app_dir / "install.json").write_text(
        json.dumps(
            {
                "app_id": "influent.demo",
                "name": "Demo",
                "version": "v1.0",
                "install_dir": str(app_dir),
                "artifact": "demo.asksome",
                "artifact_sha256": "0" * 64,
                "launcher": "launcher.py",
                "shortcuts": 5,
                "files": "launcher.py",
                "metadata": [],
            }
        ),
        encoding="utf-8",
    )

    record = read_record("influent.demo", install_root)
    assert record.shortcuts == []
    assert record.files == []
    assert record.metadata == {}

    assert uninstall_asksome("influent.demo", install_root) == [str(app_dir)]
    assert not app_dir.exists()


def test_legacy_mexf_with_wrong_section_types_is_normalized(tmp_path):
    from lib.mexf_shell import plan_from_document

    source = tmp_path / "legacy.mexf"
    source.write_text(
        json.dumps(
            {
                "extensions": 3,
                "context_menus": "not-a-list",
                "shell_commands": 5,
                "shortcuts": "not-a-dict",
                "app_name": 42,
            }
        ),
        encoding="utf-8",
    )
    document = parse_mexf(source)
    plan = plan_from_document(document.data)
    assert plan.associations == []
    assert plan.context_menus == []
    assert plan.shortcuts == {}
    assert document.metadata["name"] == "42"


@pytest.mark.parametrize(
    ("section", "value"),
    [
        ("file_associations", 5),
        ("context_menus", "texto"),
        ("registry", 1),
        ("shortcuts", [1]),
        ("environments", [1]),
        ("runtime", []),
    ],
)
def test_wrong_typed_sections_are_rejected(tmp_path, section, value):
    document = {
        "format": "mexf",
        "version": 1,
        "metadata": {"id": "demo.app", "name": "Demo", "version": "1.0"},
    }
    document[section] = value
    path = tmp_path / "bad.mexf"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(MexfError) as excinfo:
        parse_mexf(path)
    assert section in str(excinfo.value)


def test_merge_documents_normalizes_unexpected_sections():
    from lib.mexf_compiler import merge_documents

    document = MexfDocument(
        {
            "format": "mexf",
            "version": 1,
            "metadata": {"id": "a.b", "name": "A", "version": "1.0"},
            "runtime": [],
            "file_associations": 5,
            "shortcuts": [1],
            "environments": "texto",
        },
        "yaml-v1",
    )
    merged = merge_documents([document])
    assert merged["runtime"] == {}
    assert merged["file_associations"] == []
    assert merged["shortcuts"] == {}
    assert merged["environments"] == {}


def test_binary_mexf_is_reported_without_traceback(tmp_path):
    path = tmp_path / "binary.mexf"
    path.write_bytes(b"\xff\xfe\x00binario")
    assert detect_mexf_format(path) == "unknown"
    with pytest.raises(MexfError) as excinfo:
        parse_mexf(path)
    assert "UTF-8" in str(excinfo.value)


def test_yaml_with_legacy_keys_is_unknown_not_json(tmp_path):
    """R-5d1c7a83: un YAML con claves legacy no debe entregarse a ``json.loads``.

    ``detect_mexf_format`` clasificaba como ``legacy-json`` cualquier documento
    (YAML incluido) que tuviera ``extensions``/``file_associations``/
    ``context_menus`` en la raíz. ``parse_mexf`` volvía a leer el archivo como
    JSON y ``json.loads`` lanzaba ``JSONDecodeError`` fuera de ``MexfError``:
    ``--compile-mexf``, ``--shell-plan`` y ``--debug-mexf`` mostraban traceback.
    """
    path = tmp_path / "legacy-shaped.mexf"
    path.write_text(
        "extensions:\n  - extension: .foo\n    open_command: demo %1\n",
        encoding="utf-8",
    )
    assert detect_mexf_format(path) == "unknown"
    with pytest.raises(MexfError) as excinfo:
        parse_mexf(path)
    assert "desconocido" in str(excinfo.value)


def test_compile_mexf_wraps_legacy_shaped_yaml(tmp_path):
    """El compilador informa del error como ``MexfCompileError``, sin traceback."""
    from lib.mexf_compiler import MexfCompileError, compile_mexf_project

    project = tmp_path / "project"
    (project / ".mexf").mkdir(parents=True)
    (project / ".mexf" / "main.mexf").write_text(
        "file_associations:\n  - extension: .foo\n", encoding="utf-8"
    )
    (project / "details.xml").write_text(
        "<app><publisher>P</publisher><app>a</app><version>v1.0</version>"
        "<platform>AlphaCube</platform></app>",
        encoding="utf-8",
    )
    with pytest.raises(MexfCompileError) as excinfo:
        compile_mexf_project(project, tmp_path / "out.asksome")
    assert "desconocido" in str(excinfo.value)


def test_legacy_json_document_still_migrates_after_classification(tmp_path):
    """Un JSON legacy real sigue detectándose y migrando igual que antes."""
    source = tmp_path / "legacy.mexf"
    source.write_text(
        json.dumps({"app_id": "demo.app", "app_name": "Demo", "context_menus": []}),
        encoding="utf-8",
    )
    assert detect_mexf_format(source) == "legacy-json"
    document = parse_mexf(source)
    assert document.source_format == "legacy-json"
    assert document.metadata["id"] == "demo.app"
