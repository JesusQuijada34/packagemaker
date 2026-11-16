import json
import os
from pathlib import Path

import pytest

from lib.asksome_format import AsksomeError, extract_asksome, pack_asksome, verify_asksome
from lib.mexf_parser import MexfError, detect_mexf_format, migrate_legacy_mexf, parse_mexf


def test_legacy_mexf_is_detected_and_migrated(tmp_path):
    source = Path("example.mexf")
    assert detect_mexf_format(source) == "legacy-json"
    target = tmp_path / "main.mexf"
    migrate_legacy_mexf(source, target)
    document = parse_mexf(target)
    assert document.source_format == "yaml-v1"
    assert document.metadata["id"] == "com.fluthin.packagemaker"


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


def test_mexf_compiler_skips_projects_without_mexf_dir(tmp_path):
    from lib.mexf_compiler import MexfCompiler

    root = tmp_path / "plain"
    root.mkdir()
    assert MexfCompiler(root).run() is None


def test_buildthread_compiles_mexf_before_iflapp(tmp_path):
    from lib.BuildThread import FlangCompiler

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
    from lib.BuildThread import FlangCompiler

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
    from lib.asksome_installer import install_asksome, list_installed, read_record

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
    from lib.asksome_installer import install_asksome, list_installed, uninstall_asksome

    artifact, install_root, shortcuts = _install_fixture(tmp_path)
    record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    removed = uninstall_asksome(record.app_id, install_root)
    assert not Path(record.install_dir).exists()
    assert all(not Path(item).exists() for item in record.shortcuts)
    assert removed
    assert list_installed(install_root) == []


def test_uninstall_silent_on_missing(tmp_path):
    from lib.asksome_installer import AsksomeInstallError, uninstall_asksome

    assert uninstall_asksome("nope", tmp_path / "installed", silent=True) == []
    with pytest.raises(AsksomeInstallError):
        uninstall_asksome("nope", tmp_path / "installed")


def test_generated_removeme_runs_silently(tmp_path):
    import subprocess
    import sys as _sys

    from lib.asksome_installer import install_asksome

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
    from lib.asksome_format import AsksomeError
    from lib.asksome_installer import install_asksome

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
    from lib.asksome_format import verify_asksome
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
    from lib.iflapp_format import IflappSignatureError
    from lib.mexf_compiler import compile_mexf_project

    root = _make_project(tmp_path)
    result = compile_mexf_project(root, tmp_path / "enc.asksome", password="s3cret")
    with pytest.raises(IflappSignatureError):
        extract_asksome(result.output, tmp_path / "nope", password="wrong")


def test_encrypted_asksome_needs_password(tmp_path):
    from lib.iflapp_format import IflappError
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





