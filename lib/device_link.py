# -*- coding: utf-8 -*-
"""Vinculación temporal entre packagemaker.onrender.com y PackageMaker Desktop."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode

import requests

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
LINK_TTL_SECONDS = 15 * 60
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


@dataclass(frozen=True)
class AuthRequest:
    request_id: str
    state: str
    code_verifier: str
    expires_at: float


class DeviceLinkStore:
    """SQLite-backed cache for short-lived browser/device links."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS device_links (
                    request_id TEXT PRIMARY KEY,
                    state_hash TEXT NOT NULL UNIQUE,
                    code_verifier TEXT NOT NULL,
                    pairing_code TEXT UNIQUE,
                    code_hash TEXT UNIQUE,
                    session_ticket_hash TEXT UNIQUE,
                    github_access_token TEXT,
                    profile_json TEXT,
                    status TEXT NOT NULL DEFAULT 'authorizing',
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    consumed_at REAL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_device_links_code ON device_links(code_hash)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_device_links_expiry ON device_links(expires_at)"
            )

    @staticmethod
    def digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def normalize_code(code: str) -> str:
        return "".join(code.upper().split()).replace("-", "")

    @classmethod
    def code_hash(cls, code: str) -> str:
        return cls.digest(cls.normalize_code(code))

    def purge(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM device_links WHERE expires_at < ?",
                (time.time(),),
            )

    def create_auth_request(self) -> AuthRequest:
        self.purge()
        now = time.time()
        request = AuthRequest(
            request_id=secrets.token_urlsafe(18),
            state=secrets.token_urlsafe(32),
            code_verifier=secrets.token_urlsafe(48),
            expires_at=now + LINK_TTL_SECONDS,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO device_links
                    (request_id, state_hash, code_verifier, status, created_at, expires_at)
                VALUES (?, ?, ?, 'authorizing', ?, ?)
                """,
                (
                    request.request_id,
                    self.digest(request.state),
                    request.code_verifier,
                    now,
                    request.expires_at,
                ),
            )
        return request

    def get(self, request_id: str) -> Optional[sqlite3.Row]:
        self.purge()
        with self._connect() as connection:
            return connection.execute(
                "SELECT * FROM device_links WHERE request_id = ?",
                (request_id,),
            ).fetchone()

    def get_by_state(self, state: str) -> Optional[sqlite3.Row]:
        self.purge()
        with self._connect() as connection:
            return connection.execute(
                "SELECT * FROM device_links WHERE state_hash = ?",
                (self.digest(state),),
            ).fetchone()

    def get_by_code(self, code: str) -> Optional[sqlite3.Row]:
        self.purge()
        with self._connect() as connection:
            return connection.execute(
                "SELECT * FROM device_links WHERE code_hash = ?",
                (self.code_hash(code),),
            ).fetchone()

    def complete_authorization(self, request_id: str, access_token: str, profile: dict[str, Any]) -> str:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))
        display_code = f"{code[:4]}-{code[4:]}"
        ticket = secrets.token_urlsafe(32)
        now = time.time()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE device_links
                SET pairing_code = ?, code_hash = ?, session_ticket_hash = ?,
                    github_access_token = ?, profile_json = ?, status = 'ready'
                WHERE request_id = ? AND status = 'authorizing' AND expires_at >= ?
                """,
                (
                    display_code,
                    self.code_hash(display_code),
                    self.digest(ticket),
                    access_token,
                    json.dumps(profile, ensure_ascii=False),
                    request_id,
                    now,
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError("La solicitud de vinculación ya no está disponible")
        return display_code

    def fail(self, request_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE device_links SET status = 'failed' WHERE request_id = ? AND status = 'authorizing'",
                (request_id,),
            )

    def browser_status(self, request_id: str) -> dict[str, Any]:
        row = self.get(request_id)
        if row is None:
            return {"status": "expired"}
        remaining = max(0, int(float(row["expires_at"]) - time.time()))
        result: dict[str, Any] = {"status": row["status"], "expires_in": remaining}
        if row["status"] == "ready":
            result["code"] = row["pairing_code"]
        if row["status"] == "linked":
            result["profile"] = json.loads(row["profile_json"] or "{}")
        return result

    def poll_code(self, code: str) -> tuple[str, Optional[dict[str, Any]], Optional[str], Optional[int]]:
        row = self.get_by_code(code)
        if row is None:
            return "invalid", None, None, None
        remaining = max(0, int(float(row["expires_at"]) - time.time()))
        if remaining <= 0:
            return "expired", None, None, 0
        if row["status"] == "ready" and row["session_ticket_hash"]:
            ticket = secrets.token_urlsafe(32)
            # Replace the one-time server ticket hash with the returned ticket.
            with self._connect() as connection:
                cursor = connection.execute(
                    "UPDATE device_links SET session_ticket_hash = ?, status = 'linked', consumed_at = ? WHERE request_id = ? AND status = 'ready'",
                    (self.digest(ticket), time.time(), row["request_id"]),
                )
            if cursor.rowcount != 1:
                return "linked", None, None, remaining
            profile = json.loads(row["profile_json"] or "{}")
            return "complete", profile, ticket, remaining
        return row["status"], None, None, remaining

    def validate_ticket(self, ticket: str) -> tuple[Optional[dict[str, Any]], int]:
        if not ticket:
            return None, 0
        now = time.time()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM device_links WHERE session_ticket_hash = ? AND expires_at >= ? AND status = 'linked'",
                (self.digest(ticket), now),
            ).fetchone()
        if row is None:
            return None, 0
        remaining = max(0, int(float(row["expires_at"]) - now))
        return json.loads(row["profile_json"] or "{}"), remaining


def code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def build_github_url(base_url: str, request: AuthRequest) -> str:
    client_id = os.getenv("GITHUB_CLIENT_ID", "").strip()
    if not client_id:
        raise RuntimeError("GITHUB_CLIENT_ID no está configurado")
    params = {
        "client_id": client_id,
        "redirect_uri": f"{base_url.rstrip('/')}/auth/github/device-callback",
        "state": request.state,
        "code_challenge": code_challenge(request.code_verifier),
        "code_challenge_method": "S256",
        "allow_signup": "false",
    }
    return f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_github_code(base_url: str, row: sqlite3.Row, code: str) -> tuple[str, dict[str, Any]]:
    client_id = os.getenv("GITHUB_CLIENT_ID", "").strip()
    client_secret = os.getenv("GITHUB_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise RuntimeError("La OAuth App de GitHub no está configurada")
    token_response = requests.post(
        GITHUB_TOKEN_URL,
        headers={"Accept": "application/json"},
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": f"{base_url.rstrip('/')}/auth/github/device-callback",
            "code_verifier": row["code_verifier"],
        },
        timeout=15,
    )
    token_response.raise_for_status()
    access_token = token_response.json().get("access_token")
    if not access_token:
        raise RuntimeError("GitHub no devolvió una sesión válida")
    user_response = requests.get(
        GITHUB_USER_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {access_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=15,
    )
    user_response.raise_for_status()
    user = user_response.json()
    login = str(user.get("login", "")).strip()
    if not login:
        raise RuntimeError("GitHub no devolvió un usuario")
    profile = {
        "login": login,
        "id": user.get("id"),
        "name": user.get("name") or login,
        "avatar_url": user.get("avatar_url", ""),
        "html_url": user.get("html_url", f"https://github.com/{login}"),
    }
    return access_token, profile
