#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vigila la rama ``main`` del repo sin abrir el navegador.

Consulta la API de GitHub (unos pocos KB por vuelta) y avisa en la terminal
cuando aparece un commit nuevo, cuando cambia el estado de los workflows y
cuando se abre o cierra un issue/PR. Pensado para dejarlo corriendo en segundo
plano mientras se trabaja.

Ejemplos:

    export GITHUB_TOKEN=...           # o reutiliza el que ya tengas
    python scripts/watch_main.py                     # sondeo cada 60 s
    python scripts/watch_main.py --once              # una pasada y sale
    python scripts/watch_main.py --interval 30 --notify

``--notify`` intenta además una notificación nativa (``notify-send`` en Linux,
``osascript`` en macOS, ``msg`` en Windows) y cae a la terminal si no existe.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional

API = "https://api.github.com"
DEFAULT_REPO = "JesusQuijada34/packagemaker"
DEFAULT_BRANCH = "main"
TOKEN_ENV_VARS = (
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "OH_GIT_CREDENTIAL_ACCESS_TOKEN_GITHUB",
)


def token() -> Optional[str]:
    for name in TOKEN_ENV_VARS:
        value = os.environ.get(name)
        if value:
            return value
    return None


def api_get(path: str, *, timeout: float = 20.0) -> Any:
    """``GET`` a la API de GitHub con el token del entorno."""
    request = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "packagemaker-watch-main",
            **({"Authorization": f"Bearer {token()}"} if token() else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def latest_commit(repo: str, branch: str) -> Dict[str, str]:
    data = api_get(f"/repos/{repo}/commits/{branch}?per_page=1")
    return {
        "sha": data["sha"],
        "short": data["sha"][:7],
        "message": data["commit"]["message"].splitlines()[0],
        "author": data["commit"]["author"]["name"],
        "date": data["commit"]["committer"]["date"],
    }


def workflow_status(repo: str, branch: str, limit: int = 3) -> List[Dict[str, str]]:
    """Últimos ``limit`` runs de la rama (vacío si no hay Actions)."""
    try:
        data = api_get(f"/repos/{repo}/actions/runs?branch={branch}&per_page={limit}")
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 404):
            return []
        raise
    runs = []
    for run in data.get("workflow_runs", [])[:limit]:
        runs.append(
            {
                "name": run.get("name") or run.get("workflow_id", "workflow"),
                "status": run.get("status", "?"),
                "conclusion": run.get("conclusion") or "-",
                "sha": (run.get("head_sha") or "")[:7],
            }
        )
    return runs


def open_items(repo: str) -> Dict[str, int]:
    """Número de issues y PRs abiertos (dos llamadas baratas)."""
    issues = api_get(f"/repos/{repo}/issues?state=open&per_page=1")
    pulls = api_get(f"/repos/{repo}/pulls?state=open&per_page=1")
    return {
        "issues": len(issues) if isinstance(issues, list) else 0,
        "pulls": len(pulls) if isinstance(pulls, list) else 0,
    }


def notify(title: str, body: str) -> None:
    """Notificación nativa si el sistema la tiene; si no, sólo campana."""
    try:
        if shutil.which("notify-send"):
            subprocess.run(["notify-send", title, body], check=False, timeout=5)
        elif shutil.which("osascript"):
            script = f'display notification "{body}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=False, timeout=5)
        elif os.name == "nt":
            subprocess.run(
                ["msg", "*", f"{title}: {body}"], check=False, timeout=5, shell=False
            )
        else:
            sys.stdout.write("\a")
    except (OSError, subprocess.SubprocessError):
        sys.stdout.write("\a")


def stamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def report(repo: str, branch: str, *, show_items: bool) -> Dict[str, Any]:
    commit = latest_commit(repo, branch)
    state: Dict[str, Any] = {"commit": commit}
    runs = workflow_status(repo, branch)
    if runs:
        state["runs"] = runs
    if show_items:
        state["items"] = open_items(repo)
    return state


def describe(state: Dict[str, Any]) -> str:
    commit = state["commit"]
    lines = [
        f"[{stamp()}] {commit['short']}  {commit['message']}",
        f"           autor: {commit['author']}  |  fecha: {commit['date']}",
    ]
    for run in state.get("runs", []):
        lines.append(
            f"           CI {run['name']}: {run['status']}/{run['conclusion']} ({run['sha']})"
        )
    if "items" in state:
        lines.append(
            f"           abiertos: {state['items']['issues']} issues, "
            f"{state['items']['pulls']} PRs"
        )
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Vigila la rama main sin navegador.")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="owner/repo")
    parser.add_argument("--branch", default=DEFAULT_BRANCH, help="rama a vigilar")
    parser.add_argument("--interval", type=int, default=60, help="segundos entre sondeos")
    parser.add_argument("--once", action="store_true", help="una sola pasada y salir")
    parser.add_argument("--notify", action="store_true", help="notificación nativa")
    parser.add_argument(
        "--items", action="store_true", help="incluir el recuento de issues y PRs abiertos"
    )
    args = parser.parse_args(argv)

    if not token():
        print(
            "Aviso: no hay token en el entorno; la API anónima limita a 60 "
            "peticiones/hora. Exporta GITHUB_TOKEN para ir sobrado.",
            file=sys.stderr,
        )

    try:
        previous = report(args.repo, args.branch, show_items=args.items)
    except urllib.error.HTTPError as exc:
        print(f"ERROR {exc.code} al consultar {args.repo}: {exc.reason}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR de red: {exc}", file=sys.stderr)
        return 1

    print(describe(previous))
    if args.once:
        return 0

    print(f"Vigilando {args.repo}@{args.branch} cada {args.interval}s (Ctrl-C para salir).")
    try:
        while True:
            time.sleep(args.interval)
            try:
                current = report(args.repo, args.branch, show_items=args.items)
            except (urllib.error.URLError, TimeoutError) as exc:
                print(f"[{stamp()}] red intermitente: {exc}", file=sys.stderr)
                continue

            if current["commit"]["sha"] != previous["commit"]["sha"]:
                print("\n=== COMMIT NUEVO EN " + args.branch.upper() + " ===")
                print(describe(current))
                if args.notify:
                    notify("PackageMaker: commit nuevo", current["commit"]["message"])
            elif current.get("runs") != previous.get("runs"):
                print("\n=== CAMBIO EN CI ===")
                print(describe(current))

            previous = current
    except KeyboardInterrupt:
        print("\nVigilancia detenida.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
