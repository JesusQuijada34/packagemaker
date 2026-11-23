# -*- coding: utf-8 -*-
"""Integridad de ``CONFIRM.MD``, el único canal de aprobación.

R-7a3e1d92: el archivo se committeó con marcadores de conflicto de merge y la
respuesta de Q-008 quedó partida en dos, de modo que la aprobación era
ambigua. Estas comprobaciones evitan que vuelva a pasar.
"""

import re
from pathlib import Path

CONFIRM = Path(__file__).resolve().parents[1] / "CONFIRM.MD"


def _text() -> str:
    return CONFIRM.read_text(encoding="utf-8")


def test_no_merge_conflict_markers():
    text = _text()
    for marker in ("<<<<<<<", ">>>>>>>", "======="):
        assert marker not in text, f"marcador de conflicto {marker!r} en CONFIRM.MD"


def test_each_question_appears_once():
    ids = re.findall(r"^### (Q-\d{3}) ", _text(), re.MULTILINE)
    duplicates = {qid for qid in ids if ids.count(qid) > 1}
    assert not duplicates, f"preguntas duplicadas: {sorted(duplicates)}"


def test_header_records_the_last_processed_commit():
    text = _text()
    assert "Último commit de `CONFIRM.MD` procesado" in text
    assert re.search(r"\b[0-9a-f]{7,40}\b", text)


def test_pending_answers_use_one_checkbox_per_block():
    """Un bloque pendiente no puede tener ya una casilla marcada."""
    text = _text()
    pending = text.split("## Pendientes", 1)[1].split("## Historial", 1)[0]
    blocks = re.split(r"^### ", pending, flags=re.MULTILINE)[1:]
    for block in blocks:
        answers = re.findall(r"`\[[ x]\] SÍ`", block)
        assert answers, f"bloque sin casilla de respuesta: {block.splitlines()[0]}"
        marked = [a for a in answers if "[x]" in a]
        assert len(marked) <= 1, f"respuesta ambigua en: {block.splitlines()[0]}"
