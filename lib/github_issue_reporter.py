# -*- coding: utf-8 -*-
"""Reportes de bugs como issues de GitHub, firmados con el token del usuario.

Cada reporte se publica en el repositorio de PackageMaker con la cuenta de
GitHub que el usuario ya autenticó en la aplicación, así que no hay que pedir
credenciales nuevas ni mantener un servidor de telemetría.

Tres reglas gobiernan este módulo:

* **Nunca rompe la app.** Cualquier fallo de red, permisos o formato se
  convierte en un resultado con ``ok=False``; jamás en una excepción que llegue
  a la interfaz.
* **No inunda el repositorio.** Los fallos automáticos se agrupan por huella:
  si ya hay un issue abierto con la misma, se añade un comentario en vez de
  abrir otro.
* **Sin sesión no hay envío.** Si el usuario no ha iniciado sesión en GitHub el
  reporte se queda en la cola local y se reintenta más tarde; nada sale de la
  máquina sin una cuenta que lo firme.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from lib import report_telemetry

REPO = "JesusQuijada34/packagemaker"
API_ROOT = "https://api.github.com"
_USER_AGENT = "PackageMaker-BugReport"
_TIMEOUT_SECONDS = 12.0

# Etiqueta que agrupa los reportes enviados desde la aplicación. Debe existir en
# el repositorio: GitHub crea la etiqueta al vuelo si el token puede, y si no,
# el issue se abre igual sin ella.
LABEL_APP = "app-report"
LABEL_AUTO = "auto-report"

MAX_ATTACHMENT_BYTES = 2 * 1024 * 1024
MAX_ATTACHMENTS = 5

_FENCE = "```"


@dataclass
class Report:
    """Un reporte listo para publicarse."""

    title: str
    description: str
    kind: str = "bug"
    labels: List[str] = field(default_factory=list)
    attachments: List[Tuple[str, str]] = field(default_factory=list)
    environment: Optional[Dict[str, Any]] = None
    fingerprint: str = ""
    traceback_text: str = ""


@dataclass
class Result:
    ok: bool
    issue_number: int = 0
    url: str = ""
    error: str = ""
    deduplicated: bool = False

    def __bool__(self) -> bool:
        return self.ok


def _token() -> str:
    try:
        from lib.github_identity import load_token

        return str(load_token() or "")
    except Exception:
        return ""


def has_session() -> bool:
    return bool(_token())


def _request(
    method: str,
    url: str,
    token: str,
    payload: Optional[Dict[str, Any]] = None,
    *,
    timeout: float = _TIMEOUT_SECONDS,
) -> Any:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "User-Agent": _USER_AGENT,
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = json.loads(exc.read().decode("utf-8", "replace")).get("message", "")
        except Exception:
            pass
        if exc.code == 401:
            raise RuntimeError("El token de GitHub no es válido o caducó") from exc
        if exc.code == 403:
            raise RuntimeError(
                "GitHub rechazó el token (403): sin permiso para crear issues "
                "o límite de peticiones alcanzado"
            ) from exc
        if exc.code == 404:
            raise RuntimeError("No se encontró el repositorio de reportes") from exc
        raise RuntimeError(f"GitHub respondió {exc.code}: {detail}".strip()) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError("Sin conexión con GitHub") from exc
    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except ValueError as exc:
        raise RuntimeError("GitHub devolvió una respuesta que no es JSON") from exc


def _attachment_block(attachments: List[Tuple[str, str]]) -> str:
    """Adjuntos en un bloque plegable (GitHub no acepta ficheros por API)."""
    if not attachments:
        return ""
    parts = ["<details><summary>Archivos adjuntos</summary>", ""]
    for name, content in attachments[:MAX_ATTACHMENTS]:
        safe_name = re.sub(r"[^\w.\-]", "_", name)[:80] or "adjunto.txt"
        body = report_telemetry.sanitize(content)[:MAX_ATTACHMENT_BYTES]
        parts.append(f"**{safe_name}**")
        parts.append("")
        parts.append(f"{_FENCE}{safe_name.rsplit('.', 1)[-1]}")
        parts.append(body)
        parts.append(_FENCE)
        parts.append("")
    parts.append("</details>")
    return "\n".join(parts)


def build_issue_body(report: Report) -> str:
    """Cuerpo del issue: descripción, entorno y adjuntos, todo saneado."""
    environment = report.environment or report_telemetry.collect_environment()
    sections = ["## Descripción", "", report_telemetry.sanitize(report.description) or "—"]

    if report.traceback_text:
        sections += [
            "",
            "## Traza",
            "",
            f"{_FENCE}python",
            report_telemetry.sanitize(report.traceback_text),
            _FENCE,
        ]

    sections += ["", "## Entorno", "", report_telemetry.environment_markdown(environment)]

    if report.fingerprint:
        sections += ["", f"<!-- pm-fingerprint: {report.fingerprint} -->"]

    attachments = _attachment_block(report.attachments)
    if attachments:
        sections += ["", attachments]

    sections += [
        "",
        "---",
        "",
        "_Reporte enviado desde la aplicación con la cuenta de GitHub del usuario._",
    ]
    return "\n".join(sections)


def _labels_for(report: Report) -> List[str]:
    labels = [LABEL_APP]
    if report.kind and report.kind not in labels:
        labels.append(report.kind)
    if report.fingerprint:
        labels.append(LABEL_AUTO)
    labels += [label for label in report.labels if label not in labels]
    return labels


def find_open_issue(token: str, fingerprint: str) -> Optional[int]:
    """Número del issue abierto con esa huella, si ya existe."""
    if not fingerprint:
        return None
    query = f"repo:{REPO} is:issue is:open pm-fingerprint in:body"
    url = f"{API_ROOT}/search/issues?q={urllib.request.quote(query)}&per_page=20"
    try:
        payload = _request("GET", url, token)
    except RuntimeError:
        # La búsqueda puede no estar disponible (límite propio); no es motivo
        # para perder el reporte: se abre uno nuevo.
        return None
    for item in (payload or {}).get("items", []) or []:
        body = str(item.get("body", "") or "")
        if f"pm-fingerprint: {fingerprint}" in body:
            return int(item.get("number", 0) or 0)
    return None


def comment_on_issue(token: str, number: int, body: str) -> Result:
    url = f"{API_ROOT}/repos/{REPO}/issues/{number}/comments"
    try:
        payload = _request("POST", url, token, {"body": body})
    except RuntimeError as exc:
        return Result(ok=False, error=str(exc))
    return Result(ok=True, issue_number=number, url=str(payload.get("html_url", "")))


def create_issue(report: Report, *, token: str = "") -> Result:
    """Publica el reporte como issue. Agrupa los fallos repetidos."""
    token = token or _token()
    if not token:
        return Result(ok=False, error="Sin sesión de GitHub")

    body = build_issue_body(report)

    if report.fingerprint:
        existing = find_open_issue(token, report.fingerprint)
        if existing:
            comment = (
                f"Ocurrió de nuevo.\n\n{report_telemetry.environment_markdown(report.environment or {})}"
                if report.environment
                else "Ocurrió de nuevo."
            )
            result = comment_on_issue(token, existing, comment)
            result.deduplicated = True
            return result

    payload = {
        "title": report_telemetry.sanitize(report.title)[:240] or "Reporte sin título",
        "body": body,
        "labels": _labels_for(report),
    }
    try:
        created = _request("POST", f"{API_ROOT}/repos/{REPO}/issues", token, payload)
    except RuntimeError as exc:
        return Result(ok=False, error=str(exc))
    return Result(
        ok=True,
        issue_number=int(created.get("number", 0) or 0),
        url=str(created.get("html_url", "")),
    )


# ── Reportes automáticos desde el capturador de excepciones ──────────────────


def report_exception(
    exc_type: type,
    exc_value: BaseException,
    exc_tb,
    *,
    context: str = "",
    token: str = "",
) -> Result:
    """Reporta una excepción no controlada como issue agrupado por huella."""
    import traceback as _traceback

    traceback_text = "".join(_traceback.format_exception(exc_type, exc_value, exc_tb))
    name = getattr(exc_type, "__name__", str(exc_type))
    message = report_telemetry.sanitize(str(exc_value))
    environment = report_telemetry.collect_environment()

    report = Report(
        title=f"[auto] {name}: {message}"[:240],
        description=(
            f"La aplicación capturó una excepción no controlada"
            f"{' durante ' + context if context else ''}."
        ),
        kind="bug",
        labels=[LABEL_AUTO],
        environment=environment,
        fingerprint=report_telemetry.fingerprint(name, message),
        traceback_text=traceback_text,
    )
    return create_issue(report, token=token or _token())
