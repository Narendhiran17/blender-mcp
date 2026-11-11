"""Configuration management for Blender AI Control MCP Server."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BLENDER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bridge_host: str = "127.0.0.1"
    bridge_port: int = 8765
    bridge_token: Optional[str] = None
    bridge_timeout_seconds: float = 30.0
    workspace_path: Optional[str] = None
    log_level: str = "INFO"

    def get_token(self) -> str:
        """Return configured token or attempt to read token file written by add-on."""
        if self.bridge_token and self.bridge_token.strip():
            return self.bridge_token.strip()

        token_file = Path.home() / ".blender_ai_control" / "bridge_token"
        if token_file.exists():
            token = token_file.read_text(encoding="utf-8").strip()
            if token:
                return token

        return "unconfigured"


# Global settings instance
settings = Settings()
