#!/usr/bin/env python
"""Elimina UPDATER_CODE y DOCS_TEMPLATE embebidos de packagemaker.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "packagemaker.py"

HELPERS = '''
def load_updater_template():
    from lib.template_engine import load_template
    return load_template("project/updater.py.template")

def load_docs_template():
    from lib.template_engine import load_template
    return load_template("docs/index.html.template")

'''


def strip_triple_quoted_blocks(text: str, names: tuple) -> str:
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        stripped = lines[i].lstrip()
        if any(stripped.startswith(f"{name} = r'''") for name in names):
            i += 1
            while i < len(lines):
                if lines[i].rstrip().endswith("'''"):
                    i += 1
                    break
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def main():
    text = TARGET.read_text(encoding="utf-8")
    text = strip_triple_quoted_blocks(text, ("UPDATER_CODE", "DOCS_TEMPLATE"))
    if "def load_docs_template" not in text:
        text = text.replace("def getversion():", HELPERS + "def getversion():", 1)
    text = text.replace("DOCS_TEMPLATE.replace", "load_docs_template().replace")
    text = text.replace("f.write(UPDATER_CODE)", "f.write(load_updater_template())")
    TARGET.write_text(text, encoding="utf-8")
    print(f"OK: {len(text.splitlines())} lineas en packagemaker.py")


if __name__ == "__main__":
    main()
