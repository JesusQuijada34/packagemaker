"""Pruebas del shell nativo (§5.2): metadatos hover, vista previa e integración."""
import hashlib
import hmac
import json
from pathlib import Path

import pytest

from lib import asksome_format
from lib.asksome_format import pack_asksome


def _craft_signed_asksome(path, **header_extra):
    """Contenedor mínimo firmado con la clave local para probar el lector."""
    payload = b""
    header = {
        "format": "asksome",
        "format_version": 1,
        "manifest": [],
        "metadata": {},
        "compression": "lzma",
        "encryption": "none",
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
    }
    header.update(header_extra)
    signature = hmac.new(
        asksome_format.KEY, asksome_format._canonical(header) + payload, hashlib.sha256
    ).hexdigest()
    header["signature"] = signature
    header_bytes = asksome_format._canonical(header)
    Path(path).write_bytes(
        asksome_format.MAGIC + len(header_bytes).to_bytes(4, "little") + header_bytes + payload
    )
    return Path(path)


def _make_staging(tmp_path):
    staging = tmp_path / "stage"
    staging.mkdir()
    (staging / "launcher.py").write_text("print('hi')\n", encoding="utf-8")
    return staging


def test_detect_kind(tmp_path):
    from lib.native_shell import detect_kind

    staging = _make_staging(tmp_path)
    artifact = pack_asksome(staging, tmp_path / "a.asksome", metadata={"app": "x"})
    assert detect_kind(artifact) == "asksome"
    other = tmp_path / "plain.txt"
    other.write_text("nope", encoding="utf-8")
    assert detect_kind(other) == "unknown"


def test_package_info_reads_asksome_header(tmp_path):
    from lib.native_shell import package_info

    staging = _make_staging(tmp_path)
    icon = b"\x89PNG\r\n\x1a\nfakeicon"
    artifact = pack_asksome(
        staging,
        tmp_path / "a.asksome",
        metadata={"publisher": "Influent", "app": "demo", "name": "Demo", "version": "v1.0", "platform": "AlphaCube", "signer": "octocat"},
        icon=icon,
    )
    info = package_info(artifact)
    assert info["kind"] == "asksome"
    assert info["identity"]["app"] == "demo"
    assert info["identity"]["signer"] == "octocat"
    assert info["icon_bytes"] == len(icon)
    assert info["mime_type"] == "application/x-asksome"


def test_package_info_survives_encrypted_payload(tmp_path):
    from lib.native_shell import package_info

    staging = _make_staging(tmp_path)
    artifact = pack_asksome(
        staging,
        tmp_path / "enc.asksome",
        metadata={"app": "demo", "name": "Demo", "version": "v1.0"},
        password="s3cret",
        icon=b"ICON",
    )
    info = package_info(artifact)
    assert info["encryption"] != "none"
    assert info["identity"]["app"] == "demo"
    assert info["icon_bytes"] == 4


def test_package_info_rejects_unknown(tmp_path):
    from lib.native_shell import package_info

    plain = tmp_path / "plain.bin"
    plain.write_bytes(b"not a package")
    with pytest.raises(ValueError):
        package_info(plain)


def test_icon_bytes_and_preview_png_passthrough(tmp_path):
    from lib.native_shell import export_icon_preview, icon_bytes

    staging = _make_staging(tmp_path)
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 16
    artifact = pack_asksome(staging, tmp_path / "a.asksome", metadata={"app": "x"}, icon=png)
    assert icon_bytes(artifact) == png
    out = export_icon_preview(artifact, tmp_path / "previews", size=64)
    assert out is not None
    assert out.read_bytes().startswith(b"\x89PNG")


def test_export_preview_returns_none_without_icon(tmp_path):
    from lib.native_shell import export_icon_preview

    staging = _make_staging(tmp_path)
    artifact = pack_asksome(staging, tmp_path / "a.asksome", metadata={"app": "x"})
    assert export_icon_preview(artifact, tmp_path / "previews") is None


def test_write_thumbnailer_and_desktop_entry(tmp_path):
    from lib.native_shell import write_desktop_entry, write_thumbnailer

    thumbnailer = write_thumbnailer(tmp_path / "thumbnailers", python="/usr/bin/python3", root=tmp_path)
    content = thumbnailer.read_text(encoding="utf-8")
    assert "[Thumbnailer Entry]" in content
    assert "application/x-asksome" in content
    assert "application/x-iflapp" in content

    desktop = write_desktop_entry(tmp_path / "applications", exec_cmd="packagemaker")
    desktop_content = desktop.read_text(encoding="utf-8")
    assert "MimeType=application/x-iflapp;application/x-asksome;" in desktop_content


def test_install_shell_integration_freedesktop(tmp_path):
    from lib.native_shell import install_shell_integration

    result = install_shell_integration(target_dir=tmp_path, platform_name="linux")
    assert result["skipped"] == []
    written = [Path(p) for p in result["written"]]
    assert any(p.name == "packagemaker.thumbnailer" for p in written)
    assert any(p.name == "packagemaker-package.desktop" for p in written)
    assert all(p.is_file() for p in written)


def test_install_shell_integration_windows_scaffold(tmp_path):
    from lib.native_shell import install_shell_integration

    result = install_shell_integration(target_dir=tmp_path, platform_name="win32")
    assert result["written"], result
    reg = Path(result["written"][0])
    assert reg.name == "packagemaker-shell.reg"
    assert reg.read_bytes()[:2] == b"\xff\xfe"  # BOM UTF-16 LE para regedit


def test_thumbnail_main_writes_requested_output(tmp_path):
    from lib.native_shell import _thumbnail_main

    staging = _make_staging(tmp_path)
    png = b"\x89PNG\r\n\x1a\n" + b"1" * 8
    artifact = pack_asksome(staging, tmp_path / "a.asksome", metadata={"app": "x"}, icon=png)
    destination = tmp_path / "out.png"
    rc = _thumbnail_main([str(artifact), str(destination), "128"])
    assert rc == 0
    assert destination.read_bytes().startswith(b"\x89PNG")


def test_shell_info_cli_helper(tmp_path, capsys):
    from lib.cliHandler import NativeShellHelper

    staging = _make_staging(tmp_path)
    artifact = pack_asksome(
        staging,
        tmp_path / "a.asksome",
        metadata={"app": "demo", "name": "Demo", "version": "v1.0"},
        icon=b"ICON",
    )
    assert NativeShellHelper.info({"path": str(artifact), "json": True}) is True
    payload = json.loads(capsys.readouterr().out)
    assert payload["identity"]["app"] == "demo"


def test_package_info_rejects_malformed_header(tmp_path):
    from lib.native_shell import package_info

    artifact = _craft_signed_asksome(tmp_path / "bad.asksome", metadata=[])
    with pytest.raises(ValueError):
        package_info(artifact)


def test_invalid_base64_icon_does_not_break_shell_info(tmp_path):
    from lib.native_shell import icon_bytes, package_info

    artifact = _craft_signed_asksome(tmp_path / "icon.asksome", icon="abcde")
    assert icon_bytes(artifact) is None
    assert package_info(artifact)["icon_bytes"] == 0
