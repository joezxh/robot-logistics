"""Backend settings (pydantic-settings, env-prefix RCS_).

PostgreSQL only — memory/sqlite branches have been removed; the unified
async SQLAlchemy engine is the sole persistence path.
"""
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RCS_", case_sensitive=False)

    api_key: str = ""
    # Master switch for the JWT layer. When False the legacy /api/rcs/** surface
    # stays anonymous (preserving existing deployments/tests); /api/sys/** is
    # *always* authenticated regardless of this flag.
    auth_enabled: bool = False

    database_url: str = "postgresql+asyncpg://rcs:rcs@localhost:5432/rcs"

    max_shell_bounds_m: float = 500.0
    max_zones_per_shell: int = 200

    # --- System administration (rcs.sysadmin) ----------------------------
    # Secret used to sign JWTs; override via RCS_SECRET_KEY in production.
    secret_key: str = "rcs-dev-secret-key-change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # Audit logging
    audit_log_enabled: bool = True
    audit_log_batch_size: int = 20
    audit_log_flush_interval: float = 2.0
    # Comma-separated HTTP methods that must not be audited (e.g. "GET,OPTIONS").
    audit_log_skip_methods: str = "OPTIONS"
    # Request-body fields replaced with a mask before being persisted.
    audit_log_mask_fields: str = "password,oldPassword,newPassword,password_hash"
    # Paths exempt from auditing (comma-separated prefixes).
    audit_log_skip_paths: str = "/health,/docs,/openapi.json,/redoc"

    # Seed default admin/roles/menus on first boot when the tables are empty.
    sys_seed_on_startup: bool = True
    # Password assigned to seeded accounts (change immediately after first login).
    sys_default_password: str = "rcs@2026"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings