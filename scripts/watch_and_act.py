#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deja un comando corriendo y reacciona cuando ``main`` cambia.

Es ``watch_main.py`` más una acción: cuando aparece un commit nuevo puede
avisar, ejecutar la suite o pedirle a OpenHands que continúe el trabajo.

    # solo avisar (no gasta cuota ni lanza nada)
    python scripts/watch_and_act.py

    # validar cada push: corre la suite y avisa del resultado
    python scripts/watch_and_act.py --run-tests

    # pedirle a OpenHands que siga con la cola de bugs tras cada push
    python scripts/watch_and_act.py --ask "continua con la siguiente fase de bugs.md"

Las acciones se ejecutan una sola vez por commit: el SHA se guarda en
``.openhands/watch_and_act.json`` y sobrevive a reinicios del script.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import oh_chat  # noqa: E402
import watch_main  # noqa: E402

STATE_PATH = Path(".openhands/watch_and_act.json")


def load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def run_tests(root: Path) -> tuple:
    """Ejecuta la suite y devuelve ``(codigo, resumen)``."""
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    return completed.returncode, lines[-1] if lines else "(sin salida)"


def ask_agent(prompt: str, conversation_id: Optional[str]) -> str:
    """Envía ``prompt`` a la conversación y devuelve el id usado."""
    target = oh_chat.resolve_conversation(conversation_id)
    oh_chat.send_message(target, prompt)
    return target


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Vigila main y actua al cambiar.")
    parser.add_argument("--repo", default=watch_main.DEFAULT_REPO)
    parser.add_argument("--branch", default=watch_main.DEFAULT_BRANCH)
    parser.add_argument("--interval", type=int, default=120)
    parser.add_argument("--run-tests", action="store_true", help="correr la suite tras cada push")
    parser.add_argument("--ask", metavar="PROMPT", help="mensaje para OpenHands tras cada push")
    parser.add_argument("--conversation", help="id de la conversacion destino")
    parser.add_argument("--root", default=".", help="raiz del repo para las pruebas")
    parser.add_argument("--once", action="store_true", help="una pasada y salir")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    state = load_state()
    last_seen = state.get("sha")
    try:
        current = watch_main.latest_commit(args.repo, args.branch)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR de red: {exc}", file=sys.stderr)
        return 1

    print(f"[{datetime.now():%H:%M:%S}] {current['short']}  {current['message']}")
    if last_seen == current["sha"]:
        print("Sin cambios desde la ultima pasada.")
        if args.once:
            return 0
    elif last_seen:
        print(f"Nuevo desde {last_seen[:7]}: ejecutando acciones.")

    def act(commit: dict) -> None:
        if args.run_tests:
            code, summary = run_tests(root)
            print(f"  suite: {'OK' if code == 0 else 'FALLA'} -> {summary}")
            if code != 0:
                watch_main.notify("PackageMaker: tests en rojo", summary[:120])
        if args.ask:
            try:
                target = ask_agent(args.ask, args.conversation)
                print(f"  enviado a OpenHands ({target})")
            except oh_chat.ApiError as exc:
                print(f"  no se pudo enviar: {exc}", file=sys.stderr)

    if last_seen != current["sha"]:
        act(current)
        save_state({"sha": current["sha"], "at": datetime.now().isoformat(timespec="seconds")})

    if args.once:
        return 0

    print(f"Vigilando cada {args.interval}s (Ctrl-C para salir).")
    try:
        while True:
            time.sleep(args.interval)
            try:
                fresh = watch_main.latest_commit(args.repo, args.branch)
            except (urllib.error.URLError, TimeoutError) as exc:
                print(f"  red intermitente: {exc}", file=sys.stderr)
                continue
            if fresh["sha"] != current["sha"]:
                current = fresh
                print(f"\n=== NUEVO COMMIT {fresh['short']} ===\n  {fresh['message']}")
                watch_main.notify("PackageMaker: commit nuevo", fresh["message"])
                act(fresh)
                save_state(
                    {"sha": fresh["sha"], "at": datetime.now().isoformat(timespec="seconds")}
                )
    except KeyboardInterrupt:
        print("\nDetenido.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
