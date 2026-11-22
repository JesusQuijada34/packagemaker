#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Habla con OpenHands desde la terminal, sin abrir el navegador.

Tres modos:

    python scripts/oh_chat.py say "arregla el fallo de la fase 2.3"   # mensaje a esta conversacion
    python scripts/oh_chat.py read --last 5                          # ultimas respuestas
    python scripts/oh_chat.py new "revisa los tests" --repo owner/repo --branch main

La conversacion se elige con ``--conversation`` o con la variable
``OH_CONVERSATION_ID``. Sin ninguna de las dos, se usa la unica conversacion
abierta de la cuenta; si hay varias, se listan y se sale.

Credenciales: ``OPENHANDS_API_KEY`` (o ``OPENHANDS_CLOUD_API_KEY``) para la API
de la nube. La clave de sesion del sandbox se pide a la API en cada llamada y
nunca se imprime.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

BASE_URL = os.environ.get("OPENHANDS_BASE_URL", "https://app.all-hands.dev")
TOKEN_ENV_VARS = ("OPENHANDS_CLOUD_API_KEY", "OPENHANDS_API_KEY")


class ApiError(RuntimeError):
    """Fallo de la API con el código HTTP y el detalle ya legibles."""


def api_key() -> str:
    for name in TOKEN_ENV_VARS:
        value = os.environ.get(name)
        if value:
            return value
    raise ApiError(
        "Falta OPENHANDS_API_KEY (o OPENHANDS_CLOUD_API_KEY) en el entorno."
    )


def _request(
    url: str,
    *,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    payload: Any = None,
    timeout: float = 60.0,
) -> Any:
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/json",
            "User-Agent": "packagemaker-oh-chat",
            **({"Content-Type": "application/json"} if body else {}),
            **(headers or {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read()[:400].decode(errors="replace")
        raise ApiError(f"HTTP {exc.code} en {url.rsplit('/', 2)[-1]}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ApiError(f"Sin conexion con {BASE_URL}: {exc}") from exc
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw.decode(errors="replace")


def cloud(path: str, *, method: str = "GET", payload: Any = None) -> Any:
    return _request(
        f"{BASE_URL}{path}",
        method=method,
        headers={"Authorization": f"Bearer {api_key()}"},
        payload=payload,
    )


def conversation_record(conversation_id: str) -> Dict[str, Any]:
    items = cloud(f"/api/v1/app-conversations?ids={conversation_id}")
    if not isinstance(items, list) or not items:
        raise ApiError(f"No existe la conversacion {conversation_id}.")
    return items[0]


def resolve_conversation(explicit: Optional[str]) -> str:
    chosen = explicit or os.environ.get("OH_CONVERSATION_ID")
    if chosen:
        return chosen
    items = cloud("/api/v1/app-conversations/search?limit=20").get("items", [])
    running = [item for item in items if item.get("execution_status") == "running"]
    candidates = running or items
    if not candidates:
        raise ApiError("No hay conversaciones; crea una con el modo `new`.")
    if len(candidates) > 1:
        print("Hay varias conversaciones; elige con --conversation:\n", file=sys.stderr)
        for item in candidates[:10]:
            print(
                f"  {item['id']}  {item.get('execution_status', '?'):9}  "
                f"{(item.get('title') or '')[:60]}",
                file=sys.stderr,
            )
        raise ApiError("Conversacion ambigua.")
    return candidates[0]["id"]


def send_message(conversation_id: str, text: str, *, run: bool = True) -> None:
    cloud(
        f"/api/v1/app-conversations/{conversation_id}/send-message",
        method="POST",
        payload={
            "role": "user",
            "content": [{"type": "text", "text": text}],
            "run": run,
        },
    )


def agent_server(record: Dict[str, Any]) -> tuple:
    url = (record.get("conversation_url") or "").rsplit("/api/conversations", 1)[0]
    key = record.get("session_api_key")
    if not url or not key:
        raise ApiError(
            "La conversacion no expone conversation_url/session_api_key; "
            "puede estar apagada (sandbox_status="
            f"{record.get('sandbox_status')})."
        )
    return url, key


def messages(conversation_id: str, limit: int) -> List[Dict[str, str]]:
    record = conversation_record(conversation_id)
    base, session_key = agent_server(record)
    data = _request(
        f"{base}/api/conversations/{conversation_id}/events/search"
        f"?limit={limit}&kind=MessageEvent&sort_order=TIMESTAMP_DESC",
        headers={"X-Session-API-Key": session_key},
    )
    out: List[Dict[str, str]] = []
    for event in data.get("items", []):
        message = event.get("llm_message") or {}
        text = "".join(
            block.get("text", "")
            for block in message.get("content", [])
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
        if text:
            out.append(
                {
                    "role": message.get("role", "?"),
                    "source": event.get("source", "?"),
                    "timestamp": event.get("timestamp", ""),
                    "text": text,
                }
            )
    return out


def status(conversation_id: str) -> Dict[str, Any]:
    record = conversation_record(conversation_id)
    return {
        "id": record.get("id"),
        "title": record.get("title"),
        "sandbox": record.get("sandbox_status"),
        "execution": record.get("execution_status"),
        "branch": record.get("selected_branch"),
        "repo": record.get("selected_repository"),
        "ui": record.get("conversation_ui_url"),
    }


def start_conversation(
    text: str, *, repo: Optional[str], branch: Optional[str], title: Optional[str]
) -> str:
    payload: Dict[str, Any] = {
        "initial_message": {
            "role": "user",
            "content": [{"type": "text", "text": text}],
            "run": True,
        }
    }
    if repo:
        payload["selected_repository"] = repo
    if branch:
        payload["selected_branch"] = branch
    if title:
        payload["title"] = title

    started = cloud("/api/v1/app-conversations", method="POST", payload=payload)
    conversation_id = (started or {}).get("app_conversation_id")
    task_id = (started or {}).get("id")
    deadline = time.time() + 300
    while not conversation_id and task_id and time.time() < deadline:
        time.sleep(3)
        tasks = cloud(f"/api/v1/app-conversations/start-tasks?ids={task_id}")
        for task in tasks if isinstance(tasks, list) else [tasks]:
            if task and task.get("app_conversation_id"):
                conversation_id = task["app_conversation_id"]
                break
    if not conversation_id:
        raise ApiError(f"La conversacion no arranco a tiempo (start-task {task_id}).")
    return conversation_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenHands desde la terminal.")
    sub = parser.add_subparsers(dest="command", required=True)

    say = sub.add_parser("say", help="envia un mensaje a la conversacion")
    say.add_argument("text", nargs="+", help="mensaje a enviar")
    say.add_argument("--conversation", help="id de la conversacion")
    say.add_argument("--no-run", action="store_true", help="encolar sin ejecutar")
    say.add_argument("--wait", type=int, default=0, help="segundos a esperar respuesta")
    say.add_argument("--last", type=int, default=3, help="mensajes a mostrar con --wait")

    read = sub.add_parser("read", help="muestra los ultimos mensajes")
    read.add_argument("--conversation", help="id de la conversacion")
    read.add_argument("--last", type=int, default=5, help="cuantos mensajes")

    new = sub.add_parser("new", help="crea una conversacion nueva")
    new.add_argument("text", nargs="+", help="tarea inicial")
    new.add_argument("--repo", help="owner/repo")
    new.add_argument("--branch", default="main", help="rama (por defecto main)")
    new.add_argument("--title", help="titulo de la conversacion")

    info = sub.add_parser("status", help="estado de la conversacion")
    info.add_argument("--conversation", help="id de la conversacion")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "new":
            conversation_id = start_conversation(
                " ".join(args.text), repo=args.repo, branch=args.branch, title=args.title
            )
            print(f"conversacion: {conversation_id}")
            print(f"panel:        {BASE_URL}/canvas/conversations/{conversation_id}")
            return 0

        conversation_id = resolve_conversation(getattr(args, "conversation", None))

        if args.command == "say":
            send_message(conversation_id, " ".join(args.text), run=not args.no_run)
            print(f"mensaje enviado a {conversation_id}")
            if args.wait:
                time.sleep(args.wait)
                for message in reversed(messages(conversation_id, args.last)):
                    print(f"\n[{message['role']}] {message['text']}")
            return 0

        if args.command == "read":
            for message in reversed(messages(conversation_id, args.last)):
                print(f"\n[{message['role']}] {message['timestamp']}")
                print(message["text"])
            return 0

        if args.command == "status":
            for key, value in status(conversation_id).items():
                print(f"{key:10} {value}")
            return 0
    except ApiError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
