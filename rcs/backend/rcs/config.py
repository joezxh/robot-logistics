"""Backend settings (pydantic-settings, env-prefix RCS_).

PostgreSQL only — memory/sqlite branches have been removed; the unified
async SQLAlchemy engine is the sole persistence path.
"""
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RCS_", case_sensitive=False)

    api_key: str = ""
    auth_enabled: bool = False

    database_url: str = "postgresql+asyncpg://rcs:rcs@localhost:5432/rcs"

    max_shell_bounds_m: float = 500.0
    max_zones_per_shell: int = 200


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings