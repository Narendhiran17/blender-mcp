"""Authentication and token management for Blender local bridge."""

import hmac
import os
import secrets
from pathlib import Path
from typing import Optional

_ACTIVE_TOKEN: Optional[str] = None


def get_token_file_path() -> Path:
    """Return standard path to the local bridge token file."""
    token_dir = Path.home() / ".blender_ai_control"
    token_dir.mkdir(parents=True, exist_ok=True)
    return token_dir / "bridge_token"


def initialize_token(explicit_token: Optional[str] = None) -> str:
    """Initialize or load the bridge authentication token."""
    global _ACTIVE_TOKEN

    if explicit_token and explicit_token.strip():
        _ACTIVE_TOKEN = explicit_token.strip()
        return _ACTIVE_TOKEN

    env_token = os.environ.get("BLENDER_BRIDGE_TOKEN")
    if env_token and env_token.strip():
        _ACTIVE_TOKEN = env_token.strip()
        return _ACTIVE_TOKEN

    token_file = get_token_file_path()
    if token_file.exists():
        saved_token = token_file.read_text(encoding="utf-8").strip()
        if saved_token:
            _ACTIVE_TOKEN = saved_token
            return _ACTIVE_TOKEN

    # Generate new random 32-byte secure token
    new_token = secrets.token_hex(32)
    try:
        token_file.write_text(new_token, encoding="utf-8")
    except Exception as exc:
        print(f"[Blender AI Control] Warning: Could not write token file: {exc}")

    _ACTIVE_TOKEN = new_token
    return _ACTIVE_TOKEN


def get_active_token() -> str:
    """Return the currently configured active token."""
    global _ACTIVE_TOKEN
    if not _ACTIVE_TOKEN:
        _ACTIVE_TOKEN = initialize_token()
    return _ACTIVE_TOKEN


def validate_token(provided_token: Optional[str]) -> bool:
    """Safely validate provided token against active token using constant-time comparison."""
    if not provided_token:
        return False
    active = get_active_token()
    return hmac.compare_digest(active.encode("utf-8"), provided_token.strip().encode("utf-8"))
