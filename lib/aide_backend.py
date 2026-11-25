"""Backend del asistente AIDE.

AIDE no habla con un servidor propio: usa la cuenta de GitHub del usuario.
Hay dos caminos y el módulo informa de cuál está realmente disponible, sin
fingir que funciona cuando no:

``copilot``
    GitHub Copilot SDK oficial (``microsoft-copilot-sdk``). Requiere una
    suscripción de Copilot en la cuenta del usuario y que el CLI esté
    autenticado con OAuth. El SDK se ejecuta en un proceso aparte y habla por
    stdio, así que se invoca de forma síncrona desde un hilo.

``openai``
    Cualquier endpoint compatible con OpenAI (BYOK): el usuario aporta su
    propia clave y su URL. Sirve para usar Azure OpenAI, Ollama o un servidor
    local, y no depende de Copilot.

Qué sale del equipo: sólo el prompt que escribe el usuario, el contexto del
proyecto que acepte adjuntar (nombres de fichero y contenido saneado) y la
versión de la app. Nunca credenciales, rutas absolutas, ni ficheros que no se
hayan marcado. El saneado reutiliza ``lib.report_telemetry.sanitize``.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from lib.report_telemetry import sanitize

COPILOT_MODULE = "copilot"
SETTING_PROVIDER = "aide_provider"
SETTING_MODEL = "aide_model"
SETTING_ENDPOINT = "aide_endpoint"
SETTING_API_KEY = "aide_api_key"
SETTING_SEND_CONTEXT = "aide_send_context"

DEFAULT_MODEL = "gpt-5.4"


@dataclass
class Availability:
    """Estado real del proveedor, para no ofrecer lo que no se puede usar."""

    ok: bool
    reason: str = ""

    @property
    def detail(self) -> str:
        """Mensaje para registros; la interfaz usa ``reason`` y traduce."""
        return self.reason

    def __bool__(self) -> bool:
        return self.ok


@dataclass
class Answer:
    ok: bool
    text: str = ""
    error: str = ""
    provider: str = ""
    model: str = ""
    raw: Dict = field(default_factory=dict)


def _store():
    from lib.pm_data import get_pm_data

    return get_pm_data()


def get_settings() -> Dict[str, object]:
    try:
        store = _store()
        return {
            "provider": str(store.get_user(SETTING_PROVIDER, "copilot") or "copilot"),
            "model": str(store.get_user(SETTING_MODEL, DEFAULT_MODEL) or DEFAULT_MODEL),
            "endpoint": str(store.get_user(SETTING_ENDPOINT, "") or "").strip(),
            "api_key": str(store.get_user(SETTING_API_KEY, "") or ""),
            "send_context": bool(store.get_user(SETTING_SEND_CONTEXT, False)),
        }
    except Exception:
        return {
            "provider": "copilot",
            "model": DEFAULT_MODEL,
            "endpoint": "",
            "api_key": "",
            "send_context": False,
        }


def save_settings(**values: object) -> None:
    try:
        store = _store()
        for key, value in values.items():
            if key in {
                SETTING_PROVIDER,
                SETTING_MODEL,
                SETTING_ENDPOINT,
                SETTING_API_KEY,
                SETTING_SEND_CONTEXT,
            }:
                store.set_user(key, value)
        store.save()
    except Exception:
        pass


def copilot_available() -> Availability:
    """Comprueba el SDK y la sesión de GitHub sin lanzar ninguna petición."""
    try:
        __import__(COPILOT_MODULE)
    except Exception:
        return Availability(False, "missing_sdk")
    try:
        from lib import github_identity

        if not github_identity.load_token():
            return Availability(False, "no_session")
    except Exception:
        return Availability(False, "no_session")
    return Availability(True, "ready")


def openai_available(settings: Optional[Dict[str, object]] = None) -> Availability:
    settings = settings or get_settings()
    if not settings.get("endpoint"):
        return Availability(False, "no_endpoint")
    if not settings.get("api_key"):
        return Availability(False, "no_key")
    return Availability(True, "ready")


def availability(settings: Optional[Dict[str, object]] = None) -> Availability:
    settings = settings or get_settings()
    if settings.get("provider") == "openai":
        return openai_available(settings)
    return copilot_available()


def build_system_prompt(app_version: str = "") -> str:
    """Contexto fijo del repo. Nada privado: sólo reglas del proyecto."""
    version = f" (versión {app_version})" if app_version else ""
    return (
        "Eres AIDE, el asistente integrado de PackageMaker"
        f"{version}, una aplicación de escritorio en Python y PyQt6 que empaqueta "
        "proyectos en contenedores .iflapp.\n\n"
        "Responde en el idioma del usuario, de forma breve y concreta.\n"
        "Cuando propongas código, respeta estas reglas del repositorio:\n"
        "- Los nombres canónicos los genera lib/projectNameFormatter.py; nunca los "
        "compongas a mano.\n"
        "- Los colores y estilos salen de lib/design_tokens.py y de source/qss/*.qss; "
        "no escribas colores literales.\n"
        "- Cada página del sidebar es un addon declarado en addons/*.yaml.\n"
        "- Las cadenas visibles pasan por tr() y usan claves seccion.clave.\n"
        "Si no sabes algo del proyecto, dilo en vez de inventarlo."
    )


def build_context_block(files: Optional[Dict[str, str]] = None) -> str:
    """Serializa el contexto aceptado por el usuario, ya saneado."""
    if not files:
        return ""
    parts = ["Contexto del proyecto (saneado):"]
    for name, content in files.items():
        clean_name = sanitize(str(name))
        clean_body = sanitize(str(content))
        parts.append(f"\n--- {clean_name} ---\n{clean_body}")
    return "\n".join(parts)


def compose_prompt(
    message: str, files: Optional[Dict[str, str]] = None, app_version: str = ""
) -> str:
    blocks = [build_system_prompt(app_version), build_context_block(files), message]
    return "\n\n".join(block for block in blocks if block)


def ask(
    message: str,
    *,
    files: Optional[Dict[str, str]] = None,
    app_version: str = "",
    settings: Optional[Dict[str, object]] = None,
    timeout: float = 120.0,
) -> Answer:
    """Envía la consulta al proveedor configurado y devuelve su respuesta."""
    settings = settings or get_settings()
    provider = str(settings.get("provider") or "copilot")
    state = availability(settings)
    if not state.ok:
        return Answer(False, error=state.reason, provider=provider)

    prompt = compose_prompt(message, files, app_version)
    if provider == "openai":
        return _ask_openai(prompt, settings, timeout=timeout)
    return _ask_copilot(prompt, settings, timeout=timeout)


def _ask_openai(
    prompt: str, settings: Dict[str, object], *, timeout: float
) -> Answer:
    endpoint = str(settings.get("endpoint") or "").rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint = f"{endpoint}/chat/completions"
    model = str(settings.get("model") or DEFAULT_MODEL)
    payload = json.dumps(
        {"model": model, "messages": [{"role": "user", "content": prompt}]}
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.get('api_key')}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        return Answer(False, error=f"HTTP {exc.code}: {detail}", provider="openai", model=model)
    except Exception as exc:
        return Answer(False, error=str(exc), provider="openai", model=model)

    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return Answer(
            False, error="Respuesta inesperada del endpoint", provider="openai", model=model
        )
    return Answer(True, text=str(text), provider="openai", model=model, raw=data)


def _ask_copilot(
    prompt: str, settings: Dict[str, object], *, timeout: float
) -> Answer:
    """Ejecuta el SDK oficial. Devuelve el error tal cual si falla."""
    model = str(settings.get("model") or DEFAULT_MODEL)
    try:
        import asyncio

        from copilot import CopilotClient
    except Exception as exc:
        return Answer(False, error=str(exc), provider="copilot", model=model)

    async def _run() -> str:
        client = CopilotClient()
        await client.start()
        try:
            session = await client.create_session(model=model)
            response = await asyncio.wait_for(
                session.send_and_wait(prompt), timeout=timeout
            )
            data = getattr(response, "data", None)
            return str(getattr(data, "content", "") or "")
        finally:
            await client.stop()

    try:
        text = asyncio.run(_run())
    except Exception as exc:
        return Answer(False, error=str(exc), provider="copilot", model=model)
    if not text:
        return Answer(
            False, error="Copilot devolvió una respuesta vacía", provider="copilot", model=model
        )
    return Answer(True, text=text, provider="copilot", model=model)


def collect_project_context(
    root, max_files: int = 12, max_chars: int = 4000
) -> Dict[str, str]:
    """Lee los ficheros de texto de un proyecto para adjuntarlos.

    Sólo se llama cuando el usuario marca la casilla: es una lectura explícita.
    Se omiten binarios, ficheros ocultos y todo lo que supere los límites.
    """
    from pathlib import Path

    root = Path(root)
    if not root.is_dir():
        return {}
    allowed = {".py", ".json", ".xml", ".yaml", ".yml", ".md", ".txt", ".qss", ".js"}
    context: Dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if len(context) >= max_files:
            break
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        try:
            # Los ficheros enormes se descartan enteros para no leerlos en
            # memoria; los medianos se recortan a ``max_chars``.
            if path.stat().st_size > max(200_000, max_chars * 50):
                continue
            context[str(path.relative_to(root))] = path.read_text(
                encoding="utf-8", errors="replace"
            )[:max_chars]
        except Exception:
            continue
    return context


def ask_async(
    message: str,
    on_done: Callable[[Answer], None],
    *,
    files: Optional[Dict[str, str]] = None,
    app_version: str = "",
) -> None:
    """Lanza ``ask`` en un hilo daemon y entrega el resultado en *on_done*."""
    import threading

    def _worker() -> None:
        answer = ask(message, files=files, app_version=app_version)
        try:
            on_done(answer)
        except Exception:
            pass

    threading.Thread(target=_worker, name="pm-aide", daemon=True).start()
