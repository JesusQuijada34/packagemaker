"""Identidad de GitHub para firmar paquetes con el usuario autenticado.

Guarda un *token* personal (nunca en claro en los registros) y la información
pública del perfil. Con el token consulta la API de GitHub para obtener el
``login``, el nombre visible y el avatar; esos datos alimentan la firma de los
paquetes (nombre de usuario como firmante) y el panel lateral del IDE.

La red se usa sólo cuando se llama a ``fetch_profile``; el resto del módulo es
puro y verificable sin conexión.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from lib.pm_data import get_pm_data

GITHUB_API = "https://api.github.com"
_USER_AGENT = "PackageMaker-GitHubIdentity"
TOKEN_KEY = "github_token"
LOGIN_KEY = "github_login"
NAME_KEY = "github_name"
AVATAR_KEY = "github_avatar_url"
EMAIL_KEY = "github_email"

# Al copiar el token desde la web de GitHub se cuelan caracteres invisibles
# (espacio duro U+00A0, ancho cero U+200B/U+200C/U+200D, BOM U+FEFF). ``str.strip``
# no los elimina y la API responde 401 como si el token fuera inválido, o el
# cliente HTTP lanza UnicodeEncodeError al construir la cabecera.
_INVISIBLE_CHARS = dict.fromkeys(
    [0x00A0, 0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, *range(0x2000, 0x200B)]
)


def sanitize_token(token: str) -> str:
    """Limpia el token de espacios y caracteres invisibles pegados por accidente."""
    return (token or "").translate(_INVISIBLE_CHARS).strip()


class GitHubIdentityError(RuntimeError):
    """Error al resolver o validar la identidad de GitHub."""


@dataclass
class GitHubProfile:
    login: str = ""
    name: str = ""
    avatar_url: str = ""
    email: str = ""
    html_url: str = ""
    authenticated: bool = False
    extras: Dict[str, Any] = field(default_factory=dict)

    def display_name(self) -> str:
        return self.name or self.login or "Invitado"

    def signer_name(self) -> str:
        """Firmante que se incrusta en los paquetes: login de GitHub o vacío."""
        return self.login

    def signing_key(self) -> bytes:
        """Clave de firma derivada del login.

        No usa el token (secreto); sólo el ``login`` público, de modo que la
        firma sea verificable y no dependa de un credencial vivo.
        """
        return f"Influent.github.{self.login}".encode("utf-8") if self.login else b""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _store():
    return get_pm_data()


def save_token(token: str) -> None:
    store = _store()
    token = sanitize_token(token)
    if token:
        store.set_user(TOKEN_KEY, token)
    else:
        store.remove_user(TOKEN_KEY)
    store.save()


def load_token() -> str:
    return sanitize_token(str(_store().get_user(TOKEN_KEY, "") or ""))


def clear_identity() -> None:
    store = _store()
    for key in (TOKEN_KEY, LOGIN_KEY, NAME_KEY, AVATAR_KEY, EMAIL_KEY):
        store.remove_user(key)
    store.save()


def save_profile(profile: GitHubProfile) -> None:
    store = _store()
    store.set_user(LOGIN_KEY, profile.login)
    store.set_user(NAME_KEY, profile.name)
    store.set_user(AVATAR_KEY, profile.avatar_url)
    store.set_user(EMAIL_KEY, profile.email)
    store.save()


def load_profile() -> GitHubProfile:
    store = _store()
    return GitHubProfile(
        login=str(store.get_user(LOGIN_KEY, "") or ""),
        name=str(store.get_user(NAME_KEY, "") or ""),
        avatar_url=str(store.get_user(AVATAR_KEY, "") or ""),
        email=str(store.get_user(EMAIL_KEY, "") or ""),
        authenticated=bool(store.get_user(TOKEN_KEY, "")),
    )


def _request(url: str, token: str = "", *, timeout: float = 10.0) -> Any:
    headers = {"User-Agent": _USER_AGENT, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            raise GitHubIdentityError("Token de GitHub inválido o caducado") from exc
        if exc.code == 403:
            raise GitHubIdentityError(
                "GitHub rechazó el token (403): sin permisos o límite alcanzado"
            ) from exc
        if exc.code == 404:
            raise GitHubIdentityError("Recurso de GitHub no encontrado") from exc
        raise GitHubIdentityError(f"GitHub respondió {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise GitHubIdentityError("Sin conexión con GitHub") from exc
    except ValueError as exc:
        # ``http.client`` lanza ValueError/UnicodeEncodeError si la cabecera
        # lleva caracteres no ASCII (p. ej. un token pegado con un espacio duro).
        raise GitHubIdentityError(
            "El token contiene caracteres no válidos; vuelve a copiarlo sin espacios"
        ) from exc


def _profile_from_payload(payload: Dict[str, Any], *, authenticated: bool) -> GitHubProfile:
    return GitHubProfile(
        login=str(payload.get("login", "") or ""),
        name=str(payload.get("name", "") or ""),
        avatar_url=str(payload.get("avatar_url", "") or ""),
        email=str(payload.get("email", "") or ""),
        html_url=str(payload.get("html_url", "") or ""),
        authenticated=authenticated,
        extras={"public_repos": payload.get("public_repos", 0)},
    )


def fetch_profile(token: str = "", *, timeout: float = 10.0) -> GitHubProfile:
    """Obtiene el perfil autenticado (``/user``) o público por ``login``."""
    token = sanitize_token(token or load_token())
    if token:
        payload = _request(f"{GITHUB_API}/user", token, timeout=timeout)
        profile = _profile_from_payload(payload, authenticated=True)
        save_profile(profile)
        return profile

    login = load_profile().login
    if not login:
        raise GitHubIdentityError("No hay token ni login de GitHub configurado")
    payload = _request(f"{GITHUB_API}/users/{login}", timeout=timeout)
    profile = _profile_from_payload(payload, authenticated=False)
    save_profile(profile)
    return profile


def fetch_avatar(profile: GitHubProfile, *, timeout: float = 15.0) -> Optional[bytes]:
    """Descarga los bytes del avatar del perfil (para el panel lateral)."""
    if not profile.avatar_url:
        return None
    request = urllib.request.Request(profile.avatar_url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def signer_from_store() -> str:
    """Nombre de firmante guardado, o cadena vacía si no hay sesión."""
    return str(_store().get_user(LOGIN_KEY, "") or "")


def _avatar_cache_path(login: str) -> Path:
    return _avatar_cache_dir() / f"{login}.img"


def _avatar_cache_dir() -> Path:
    from lib.pm_data import _data_dir

    directory = _data_dir() / "avatars"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def cache_avatar(login: str, data: bytes) -> Optional[Path]:
    """Guarda el avatar en caché local para no volver a descargarlo."""
    if not login or not data:
        return None
    path = _avatar_cache_path(login)
    path.write_bytes(data)
    return path


def load_cached_avatar(login: str) -> Optional[bytes]:
    """Devuelve los bytes del avatar en caché, o ``None`` si no existe."""
    if not login:
        return None
    path = _avatar_cache_path(login)
    try:
        return path.read_bytes() if path.is_file() else None
    except OSError:
        return None


def apply_signer(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Inyecta el firmante de GitHub en los metadatos si hay sesión.

    Respeta un ``signer`` explícito en los metadatos; sólo rellena el hueco.
    """
    signer = signer_from_store()
    if signer and not metadata.get("signer"):
        metadata = dict(metadata)
        metadata["signer"] = signer
    return metadata
