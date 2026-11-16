"""Compilador de proyectos ``.mexf`` a artefactos ``.asksome``.

Encadena la lectura de ``details.xml``, el parseo y la validación de
``.mexf/main.mexf`` junto con sus submódulos, y el empaquetado determinista del
contenedor ``.asksome`` (cabecera firmada + payload comprimido).

El resultado es reproducible: los mismos módulos y assets producen bytes
idénticos, porque el manifiesto y el payload se ordenan de forma estable y no
se incrustan marcas de tiempo.
"""
from __future__ import annotations

import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from lib.asksome_format import pack_asksome
from lib.mexf_parser import (
    Diagnostic,
    MexfDocument,
    MexfError,
    canonicalize_mexf,
    parse_mexf,
    validate_mexf,
)

MEXF_DIRNAME = ".mexf"
MAIN_MEXF_NAME = "main.mexf"
LAUNCHER_NAME = "launcher.py"

_LIST_SECTIONS = ("triggers", "commands", "assets", "file_associations", "context_menus")
_DICT_SECTIONS = ("shortcuts", "environments")

_LAUNCHER_SOURCE = '''"""Launcher generado por PackageMaker para un artefacto .asksome."""
import json
import sys
from pathlib import Path


def load_plan(root):
    return json.loads((Path(root) / "main.mexf").read_text(encoding="utf-8"))


def main(argv=None):
    root = Path(__file__).resolve().parent
    plan = load_plan(root)
    metadata = plan.get("metadata", {})
    print(f"{metadata.get('name', 'mexf')} {metadata.get('version', '')}".strip())
    print(f"triggers={len(plan.get('triggers', []))} commands={len(plan.get('commands', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
'''


class MexfCompileError(ValueError):
    """Error al compilar un proyecto ``.mexf``."""


@dataclass
class CompileResult:
    output: Path
    modules: List[str] = field(default_factory=list)
    diagnostics: List[Diagnostic] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    wrappers: List[Path] = field(default_factory=list)


def read_project_details(project_root: Path | str) -> Dict[str, Any]:
    """Extrae los metadatos de ``details.xml`` con los mismos alias que el build."""
    root = Path(project_root)
    details = root / "details.xml"
    if not details.is_file():
        raise MexfCompileError(f"No se encontró details.xml en {root}")
    try:
        node = ET.parse(details).getroot()
    except ET.ParseError as exc:
        raise MexfCompileError(f"details.xml inválido: {exc}") from exc
    return {
        "publisher": node.findtext("publisher") or node.findtext("empresa") or "Unknown",
        "app": node.findtext("app") or node.findtext("name") or "Unknown",
        "name": node.findtext("name") or node.findtext("titulo") or "Unknown",
        "version": node.findtext("version") or "v1.0",
        "platform": node.findtext("platform") or node.findtext("plataforma") or "AlphaCube",
        "author": node.findtext("author") or node.findtext("autor") or "Unknown",
    }


def discover_mexf_modules(project_root: Path | str) -> List[Path]:
    """Devuelve ``main.mexf`` primero y luego los submódulos, ordenados."""
    mexf_dir = Path(project_root) / MEXF_DIRNAME
    if not mexf_dir.is_dir():
        raise MexfCompileError(f"No existe el directorio {MEXF_DIRNAME}/ en {project_root}")
    main = mexf_dir / MAIN_MEXF_NAME
    if not main.is_file():
        raise MexfCompileError(f"Falta {MEXF_DIRNAME}/{MAIN_MEXF_NAME}")
    modules = [main]
    modules.extend(sorted(path for path in mexf_dir.rglob("*.mexf") if path != main))
    return modules


def merge_documents(documents: List[MexfDocument]) -> Dict[str, Any]:
    """Funde los módulos en un único documento; ``main.mexf`` tiene prioridad."""
    if not documents:
        raise MexfCompileError("No hay documentos .mexf que fusionar.")
    base = documents[0].data
    merged: Dict[str, Any] = {
        "format": "mexf",
        "version": 1,
        "metadata": dict(base.get("metadata", {})),
        "runtime": dict(base.get("runtime", {})),
    }
    for section in _LIST_SECTIONS:
        merged[section] = list(base.get(section, []))
    for section in _DICT_SECTIONS:
        merged[section] = dict(base.get(section, {}))
    for document in documents[1:]:
        data = document.data
        for section in _LIST_SECTIONS:
            extra = data.get(section, [])
            if isinstance(extra, list):
                merged[section].extend(extra)
        for section in _DICT_SECTIONS:
            extra = data.get(section, {})
            if isinstance(extra, dict):
                merged[section].update(extra)
    return merged


def _apply_details_defaults(merged: Dict[str, Any], details: Dict[str, Any]) -> None:
    metadata = merged.setdefault("metadata", {})
    metadata.setdefault("id", f"{details['publisher']}.{details['app']}".lower())
    metadata.setdefault("name", details["name"])
    metadata.setdefault("version", details["version"])


def _stage_assets(project_root: Path, staging: Path, merged: Dict[str, Any]) -> None:
    root = project_root.resolve()
    for index, asset in enumerate(merged.get("assets", [])):
        if not isinstance(asset, dict) or not isinstance(asset.get("path"), str):
            raise MexfCompileError(f"assets[{index}] necesita un path válido.")
        relative = asset["path"].replace("\\", "/")
        source = (root / relative).resolve()
        if root not in source.parents and source != root:
            raise MexfCompileError(f"asset fuera de la raíz del proyecto: {relative}")
        if not source.is_file():
            raise MexfCompileError(f"asset no encontrado: {relative}")
        target = staging / "assets" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())


def _stage_project(project_root: Path, staging: Path, merged: Dict[str, Any]) -> None:
    staging.mkdir(parents=True, exist_ok=True)
    (staging / "main.mexf").write_bytes(canonicalize_mexf(merged))
    (staging / LAUNCHER_NAME).write_text(_LAUNCHER_SOURCE, encoding="utf-8")
    details = project_root / "details.xml"
    if details.is_file():
        (staging / "details.xml").write_bytes(details.read_bytes())
    _stage_assets(project_root, staging, merged)


_SYNTAX_WRAPPER = '''#!/usr/bin/env python3
"""Envoltorio de prueba de sintaxis para {name}.

Verifica que el artefacto {artifact} tenga cabecera válida y firma correcta sin
extraer ni ejecutar el payload.
"""
import sys
from pathlib import Path

ARTIFACT = Path(__file__).with_name({artifact!r})


def main():
    from lib.asksome_format import AsksomeError, verify_asksome

    if not ARTIFACT.is_file():
        print(f"[syntax] falta el artefacto: {{ARTIFACT}}", file=sys.stderr)
        return 1
    try:
        header = verify_asksome(ARTIFACT)
    except AsksomeError as exc:
        print(f"[syntax] cabecera inválida: {{exc}}", file=sys.stderr)
        return 1
    modules = header.get("metadata", {{}}).get("modules", [])
    print(f"[syntax] OK {{len(modules)}} módulo(s): {{', '.join(modules)}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

_ENV_WRAPPER = '''#!/usr/bin/env python3
"""Envoltorio de prueba de entorno para {name}.

Comprueba que el intérprete y la plataforma declarada sean compatibles con el
artefacto antes de instalarlo.
"""
import platform
import sys
from pathlib import Path

ARTIFACT = Path(__file__).with_name({artifact!r})
EXPECTED_PLATFORM = {platform!r}


def main():
    from lib.asksome_format import verify_asksome

    print(f"[env] python {{sys.version.split()[0]}} en {{platform.system()}}")
    header = verify_asksome(ARTIFACT)
    declared = header.get("metadata", {{}}).get("platform", "")
    if EXPECTED_PLATFORM and declared != EXPECTED_PLATFORM:
        print(f"[env] plataforma declarada {{declared}} != {{EXPECTED_PLATFORM}}", file=sys.stderr)
        return 1
    print(f"[env] OK plataforma {{declared}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _find_project_icon(project_root: Path, app: str) -> Optional[bytes]:
    """Busca un icono del proyecto para incrustarlo en claro en la cabecera.

    Prioriza el icono específico de la app sobre el genérico y ``.ico`` sobre
    ``.png``, igual que hace el resto del build.
    """
    stems = [f"{app}-icon", "app-icon", "icon"]
    for directory in (project_root / "app", project_root):
        for stem in stems:
            for ext in (".ico", ".png"):
                candidate = directory / f"{stem}{ext}"
                if candidate.is_file():
                    return candidate.read_bytes()
    return None


def write_test_wrappers(
    merged: Dict[str, Any],
    output: Path,
    metadata: Dict[str, Any],
) -> List[Path]:
    """Escribe los envoltorios de prueba de sintaxis y entorno junto al artefacto.

    Se ejecutan antes del build del ``.iflapp`` para detectar un ``.asksome``
    corrupto o una plataforma incompatible sin instalar nada.
    """
    output = Path(output)
    name = metadata.get("name") or metadata.get("app") or "asksome"
    artifact = output.name
    platform_name = metadata.get("platform", "")
    written: List[Path] = []
    for suffix, template in (("check-syntax.py", _SYNTAX_WRAPPER), ("check-env.py", _ENV_WRAPPER)):
        wrapper = output.with_name(f"{output.stem}.{suffix}")
        wrapper.write_text(
            template.format(name=name, artifact=artifact, platform=platform_name),
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        written.append(wrapper)
    return written


def compile_mexf_project(
    project_root: Path | str,
    output_file: Path | str | None = None,
    *,
    staging_dir: Path | str | None = None,
    password: str | None = None,
    wrappers: bool = False,
) -> CompileResult:
    """Compila un proyecto ``.mexf`` a un ``.asksome`` firmado.

    Sigue la jerarquía: ``details.xml`` → ``.mexf/main.mexf`` → submódulos.
    Con ``password`` el payload viaja cifrado (cabecera en claro, payload no).
    Con ``wrappers`` se emiten además los envoltorios de prueba de sintaxis y
    entorno junto al artefacto.
    """
    root = Path(project_root).resolve()
    details = read_project_details(root)
    modules = discover_mexf_modules(root)
    try:
        documents = [parse_mexf(module, project_root=root) for module in modules]
    except MexfError as exc:
        raise MexfCompileError(str(exc)) from exc
    merged = merge_documents(documents)
    _apply_details_defaults(merged, details)

    diagnostics = validate_mexf(merged, project_root=root)
    errors = [item for item in diagnostics if item.severity == "error"]
    if errors:
        raise MexfCompileError("; ".join(f"{item.path}: {item.message}" for item in errors))

    module_names = [module.relative_to(root).as_posix() for module in modules]
    metadata = {
        "id": merged["metadata"]["id"],
        "name": merged["metadata"]["name"],
        "version": merged["metadata"]["version"],
        "publisher": details["publisher"],
        "app": details["app"],
        "platform": details["platform"],
        "author": details["author"],
        "modules": module_names,
    }

    output = Path(output_file) if output_file else root / f"{details['app']}.asksome"

    icon = _find_project_icon(root, details["app"])
    if staging_dir is not None:
        _stage_project(root, Path(staging_dir), merged)
        pack_asksome(staging_dir, output, metadata=metadata, launcher=LAUNCHER_NAME, password=password, icon=icon)
    else:
        with tempfile.TemporaryDirectory(prefix="mexf-build-") as tmp:
            _stage_project(root, Path(tmp), merged)
            pack_asksome(tmp, output, metadata=metadata, launcher=LAUNCHER_NAME, password=password, icon=icon)

    result = CompileResult(
        output=output,
        modules=module_names,
        diagnostics=diagnostics,
        metadata=metadata,
    )
    if wrappers:
        result.wrappers = write_test_wrappers(merged, output, metadata)
    return result


class MexfCompiler:
    """Envoltorio con log y procedimiento, para encadenarlo al build del ``.iflapp``."""

    def __init__(
        self,
        project_root: Path | str,
        output_path: Path | str | None = None,
        log_callback=None,
        password: str | None = None,
        wrappers: bool = False,
    ):
        self.project_root = Path(project_root).resolve()
        self.output_path = Path(output_path).resolve() if output_path else None
        self.log_callback = log_callback
        self.password = password
        self.wrappers = wrappers
        self.last_error = ""
        self.procedure: List[str] = []

    def log(self, message: str) -> None:
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def _record(self, step: str) -> None:
        self.procedure.append(step)

    def run(self) -> Optional[Path]:
        if not (self.project_root / MEXF_DIRNAME).is_dir():
            return None
        try:
            details = read_project_details(self.project_root)
            modules = discover_mexf_modules(self.project_root)
            self._record(f"Leer details.xml ({details['publisher']}/{details['app']})")
            self._record(
                "Procesar .mexf: " + ", ".join(str(m.relative_to(self.project_root)) for m in modules)
            )
            output = None
            if self.output_path is not None:
                output = self.output_path / f"{details['app']}.asksome"
            result = compile_mexf_project(
                self.project_root,
                output,
                password=self.password,
                wrappers=self.wrappers,
            )
        except MexfCompileError as exc:
            self.last_error = str(exc)
            self.log(f"[ERROR] Compilación .mexf fallida: {exc}")
            return None
        self._record(f"Empaquetar .asksome firmado: {result.output.name}")
        if result.wrappers:
            self._record(
                "Generar envoltorios de prueba: "
                + ", ".join(wrapper.name for wrapper in result.wrappers)
            )
        self.log(f"[INFO] .asksome generado: {result.output}")
        return result.output
