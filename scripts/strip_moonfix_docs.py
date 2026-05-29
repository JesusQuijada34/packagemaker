#!/usr/bin/env python
"""Elimina DOCS_TEMPLATE embebido de lib/moonFixWizard.py."""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "lib" / "moonFixWizard.py"


def main():
    text = TARGET.read_text(encoding="utf-8")
    start = text.find("DOCS_TEMPLATE = r'''")
    end = text.find("class MoonFixWizard(QDialog):")
    if start == -1 or end == -1:
        raise SystemExit("Marcadores no encontrados en moonFixWizard.py")
    text = text[:start] + text[end:]
    if "# Constants" in text[:start]:
        text = text.replace("# Constants\n", "", 1)
    TARGET.write_text(text, encoding="utf-8")
    print(f"OK: {len(text.splitlines())} lineas")


if __name__ == "__main__":
    main()
