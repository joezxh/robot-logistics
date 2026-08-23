"""Backend settings (pydantic-settings, env-prefix RCS_)."""
from __future__ import annotations
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RCS_", case_sensitive=False)

    # Auth
    api_key: str = ""
    auth_enabled: bool = False

    # Storage
    storage: Literal["memory", "sqlite"] = "memory"
    db_path: str = "/tmp/rcs.db"

    # Integration with rcs/rcs/ subproject
    embedded: bool = False
    service_url: str = "http://127.0.0.1:8101"
    service_timeout_s: float = 5.0

    # Topology limits
    max_shell_bounds_m: float = 500.0
    max_zones_per_shell: int = 200


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
