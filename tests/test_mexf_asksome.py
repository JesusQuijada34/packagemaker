import json
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


