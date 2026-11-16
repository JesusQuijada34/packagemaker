import json
from pathlib import Path

import pytest

from lib.asksome_format import AsksomeError, extract_asksome, pack_asksome, read_asksome_header, verify_asksome
from lib.mexf_parser import MexfError, canonicalize_mexf, detect_mexf_format, migrate_legacy_mexf, parse_mexf


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
