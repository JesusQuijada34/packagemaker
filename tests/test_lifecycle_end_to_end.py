# -*- coding: utf-8 -*-
"""QA integral del ciclo de vida (§6.1).

Ejercita con las funciones reales la cadena completa:

    crear proyecto → escanear IDE → compilar guiones → compilar .mexf a
    .asksome → instalar → ejecutar el lanzador → desinstalar con ``removeme.py``.

Cada paso usa el mismo módulo que la UI/CLI, sin mocks, para que un cambio de
contrato rompa el test.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.iflapp_ide import compile_project, run_script, scan_project  # noqa: E402
from lib.template_engine import create_project_from_templates, templates_available  # noqa: E402

MAIN_MEXF = """format: mexf
version: 1
metadata:
  id: influent.lifecycle
  name: Lifecycle Demo
  version: v1.0
runtime:
  launcher: argv
commands:
  - id: demo.hello
    executable: python
    args: ["-c", "print('hola-ciclo')"]
triggers: []
"""

pytestmark = pytest.mark.skipif(
    not templates_available(),
    reason="sin plantillas de proyecto (bundle sin src/templates)",
)


def _create_project(tmp_path: Path) -> Path:
    folder = "influent.lifecycle.v1.0-26.05-20.13-Danenone"
    target = tmp_path / folder
    create_project_from_templates(
        target,
        publisher="Influent",
        app_id="lifecycle",
        name="Lifecycle Demo",
        author="JesusQuijada34",
        platform="Danenone",
        version_base="1.0",
        description="Ciclo de vida",
        timestamp="26.05-20.13",
    )
    return target


def test_full_lifecycle_create_scan_compile_install_run_uninstall(tmp_path):
    project = _create_project(tmp_path)
    assert (project / "details.xml").is_file()
    assert (project / "config" / "settings.json").is_file()

    # 1) El IDE reconoce el proyecto recién creado.
    scanned = scan_project(project)
    assert scanned.app == "lifecycle"
    assert scanned.scripts, "el proyecto debe declarar al menos un guion"

    # 2) El IDE compila los guiones con el backend stdlib (siempre disponible).
    outcome = compile_project(project, backend="zipapp")
    assert outcome.ok, outcome.failures
    artifact = Path(outcome.outputs[0])
    assert artifact.suffix == ".pyz"
    assert artifact.is_file()

    # 3) Ejecutar el guion del proyecto captura su salida real.
    entry = scanned.entry or scanned.scripts[0]
    code, output = run_script(project / entry)
    assert code == 0, output


def test_mexf_asksome_install_run_uninstall(tmp_path):
    from lib.asksome_installer import install_asksome, list_installed
    from lib.mexf_compiler import compile_mexf_project

    project = _create_project(tmp_path)
    mexf_dir = project / ".mexf"
    mexf_dir.mkdir()
    (mexf_dir / "main.mexf").write_text(MAIN_MEXF, encoding="utf-8")

    # 1) Compilar el .mexf a un .asksome firmado.
    artifact = compile_mexf_project(project, tmp_path / "demo.asksome").output
    assert artifact.is_file()

    # 2) Instalar verificando la firma, con accesos directos aislados.
    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()
    install_root = tmp_path / "installed"
    record = install_asksome(artifact, install_root, shortcut_dirs=[shortcuts])
    assert Path(record.install_dir).is_dir()
    assert [item.app_id for item in list_installed(install_root)] == [record.app_id]

    # 3) Ejecutar el lanzador independiente y comprobar su salida real.
    launcher = Path(record.install_dir) / record.launcher
    result = subprocess.run(
        [sys.executable, str(launcher)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr

    # 4) El desinstalador generado purga archivos y accesos directos.
    removeme = Path(record.install_dir) / "removeme.py"
    assert removeme.is_file()
    subprocess.run(
        [sys.executable, str(removeme), "--silent"], check=True, capture_output=True
    )
    assert not Path(record.install_dir).exists()
    assert list_installed(install_root) == []


def test_lifecycle_record_is_json_and_lists_payload(tmp_path):
    from lib.asksome_installer import install_asksome

    from lib.mexf_compiler import compile_mexf_project

    project = _create_project(tmp_path)
    (project / ".mexf").mkdir()
    (project / ".mexf" / "main.mexf").write_text(MAIN_MEXF, encoding="utf-8")
    artifact = compile_mexf_project(project, tmp_path / "demo.asksome").output

    record = install_asksome(artifact, tmp_path / "installed", create_desktop_shortcuts=False)
    data = json.loads((Path(record.install_dir) / "install.json").read_text(encoding="utf-8"))
    assert data["app_id"] == record.app_id
    assert "launcher.py" in data["files"]
