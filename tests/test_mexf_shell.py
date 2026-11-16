# -*- coding: utf-8 -*-
"""Shell nuevo declarado en YAML ``.mexf`` (sustituye al shell antiguo)."""
import json
from pathlib import Path


from lib.mexf_parser import parse_mexf
from lib.mexf_shell import (
    install_plan,
    load_shell_plan,
    plan_from_document,
    render_desktop_entries,
    render_mime_xml,
    render_registry,
    render_servicemenus,
    uninstall_plan,
)

ROOT = Path(__file__).resolve().parents[1]

MEXF = """format: mexf
version: 1
metadata:
  id: influent.shell
  name: Shell Demo
  version: v1.0
icon: app/app-icon.ico
file_associations:
  - extension: .iflapp
    prog_id: InfluentPackage
    description: Fluthin Package
    default_icon: app/app-icon.ico
    open_command: packagemaker --open-package "%1"
context_menus:
  - target: file
    extensions: [".iflapp"]
    label: Instalar Paquete
    command: packagemaker --install-package "%1"
  - target: folder
    label: Crear Proyecto Aquí
    command: packagemaker --create-project "%1"
shortcuts:
  desktop: true
  start_menu: true
environments:
  IPM_HOME: /opt/ipm
registry:
  - root: HKEY_CLASSES_ROOT
    path: .iflapp
    values:
      "": InfluentPackage
"""


def _plan(tmp_path):
    path = tmp_path / "main.mexf"
    path.write_text(MEXF, encoding="utf-8")
    return load_shell_plan(path)


def test_shell_plan_reads_yaml_sections(tmp_path):
    plan = _plan(tmp_path)
    assert plan.identifier == "influent.shell"
    assert [a.extension for a in plan.associations] == [".iflapp"]
    assert plan.associations[0].mime_type == "application/x-iflapp"
    assert [m.label for m in plan.context_menus] == ["Instalar Paquete", "Crear Proyecto Aquí"]
    assert plan.environments == {"IPM_HOME": "/opt/ipm"}


def test_plan_from_document_defaults_mime_type():
    plan = plan_from_document(
        {
            "metadata": {"id": "x.y", "name": "Y"},
            "file_associations": [{"extension": "demo"}],
        }
    )
    assert plan.associations[0].extension == ".demo"
    assert plan.associations[0].mime_type == "application/x-demo"


def test_render_mime_xml_declares_globs(tmp_path):
    xml = render_mime_xml(_plan(tmp_path))
    assert 'type="application/x-iflapp"' in xml
    assert 'glob pattern="*.iflapp"' in xml


def test_render_desktop_entries_translate_exec_markers(tmp_path):
    entries = render_desktop_entries(_plan(tmp_path))
    body = next(iter(entries.values()))
    assert "MimeType=application/x-iflapp;" in body
    assert "%f" in body and "%1" not in body


def test_render_servicemenus_uses_directory_for_folder_targets(tmp_path):
    menus = render_servicemenus(_plan(tmp_path))
    joined = "\n".join(menus.values())
    assert "inode/directory;" in joined
    assert "KonqPopupMenu/Plugin" in joined


def test_render_registry_includes_associations_and_environment(tmp_path):
    reg = render_registry(_plan(tmp_path))
    assert r"[HKEY_CLASSES_ROOT\.iflapp]" in reg
    assert r"[HKEY_CLASSES_ROOT\Directory\shell\Crear-Proyecto-Aqu" in reg
    assert "[HKEY_CURRENT_USER\\Environment]" in reg
    assert "IPM_HOME" in reg


def test_install_and_uninstall_plan_round_trip(tmp_path):
    plan = _plan(tmp_path)
    base = tmp_path / "share"
    written = install_plan(plan, base_dir=base, platform_name="linux")["written"]
    assert written
    for path in written:
        assert Path(path).exists()
    removed = uninstall_plan(plan, base_dir=base, platform_name="linux")["removed"]
    assert removed
    for path in removed:
        assert not Path(path).exists()


def test_install_plan_windows_writes_utf16_reg(tmp_path):
    plan = _plan(tmp_path)
    result = install_plan(plan, base_dir=tmp_path / "win", platform_name="win32")
    reg = Path(result["written"][0])
    assert reg.read_text(encoding="utf-16").startswith("Windows Registry Editor")


def test_shipped_example_mexf_yields_shell_plan():
    plan = load_shell_plan(ROOT / "example.mexf")
    assert plan.identifier == "com.fluthin.packagemaker"
    assert {a.extension for a in plan.associations} == {".iflapp", ".mexf"}
    assert any(m.target == "background" for m in plan.context_menus)


def test_shell_plan_json_cli_helper(tmp_path, capsys):
    from lib.cliHandler import MexfShellHelper

    path = tmp_path / "main.mexf"
    path.write_text(MEXF, encoding="utf-8")
    assert MexfShellHelper.plan({"path": str(path), "json": True})
    payload = json.loads(capsys.readouterr().out)
    assert payload["id"] == "influent.shell"


def test_parse_mexf_still_accepts_plan_document(tmp_path):
    path = tmp_path / "main.mexf"
    path.write_text(MEXF, encoding="utf-8")
    assert parse_mexf(path).metadata["id"] == "influent.shell"
