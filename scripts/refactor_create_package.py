#!/usr/bin/env python
"""Reemplaza el bloque inline de creacion de paquete por template_engine."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "packagemaker.py"

FOLDER_BLOCK = """        folder_name = f\"{empresa}.{nombre_logico}.v{version}\"
        full_path = os.path.join(BASE_DIR, folder_name)"""

FOLDER_BLOCK_NEW = """        version_base = (self.input_version.text().strip() or \"1\").split(\"-\")[0]
        from lib.template_engine import build_variables

        _vars = build_variables(
            empresa, nombre_logico, nombre_completo, autor, plataforma_seleccionada, version_base
        )
        folder_name = f\"{empresa}.{nombre_logico}.v{_vars['VERSION_FULL']}\"
        full_path = os.path.join(BASE_DIR, folder_name)
        hv = _vars[\"CORRELATIONID\"]"""

START = "            for folder in DEFAULT_FOLDERS.split(\",\"):"
END = "            icon_dest = os.path.join(full_path, \"app\", \"app-icon.ico\")"

REPLACEMENT = """            from pathlib import Path as _Path
            from lib.template_engine import create_project_from_templates

            os.makedirs(full_path, exist_ok=True)
            create_project_from_templates(
                _Path(full_path),
                empresa,
                nombre_logico,
                nombre_completo,
                autor,
                plataforma_seleccionada,
                version_base=version_base,
            )
"""

TAIL_START = "            requirements_path = os.path.join(full_path, \"lib\", \"requirements.txt\")"
TAIL_END = "            self.create_status.setStyleSheet(\"color:#388e3c;\")"


def main():
    text = TARGET.read_text(encoding="utf-8")
    if FOLDER_BLOCK not in text:
        raise SystemExit("Bloque folder_name no encontrado")
    text = text.replace(FOLDER_BLOCK, FOLDER_BLOCK_NEW, 1)
    start_idx = text.find(START)
    end_idx = text.find(END)
    if start_idx == -1 or end_idx == -1:
        raise SystemExit(f"Marcadores no encontrados: start={start_idx}, end={end_idx}")
    text = text[:start_idx] + REPLACEMENT + text[end_idx:]
    t_start = text.find(TAIL_START)
    t_end = text.find(TAIL_END)
    if t_start != -1 and t_end != -1:
        text = text[:t_start] + text[t_end:]
    TARGET.write_text(text, encoding="utf-8")
    print("OK: bloque create_package refactorizado")


if __name__ == "__main__":
    main()
