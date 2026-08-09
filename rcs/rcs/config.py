"""RCS autonomous configuration.

RCS is a self-contained subproject: it owns its auth policy, service binding and
MQTT adapter settings. It deliberately does NOT import the simulation backend's
settings so the dependency direction stays one-way (rcs -> shared, never
rcs -> simulation).

All values are overridable via environment variables (prefix ``RCS_``) or a
``.env`` file placed next to the running process.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class RCSSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RCS_", env_file=".env", extra="ignore")

    app_name: str = "RCS - Robot Control System"
    log_level: str = "INFO"

    # --- Standalone service binding (ignored in embedded mode) ---
    host: str = "127.0.0.1"
    port: int = 8100
    # CORS origins for the standalone app, comma separated. "*" allows all.
    cors_origins: str = "*"

    # --- Auth (mirrors the simulation backend's policy but owned by RCS) ---
    api_auth_enabled: bool = False
    api_keys: str = ""
    rate_limit_max: int = 120
    rate_limit_window_seconds: float = 60.0

    # --- MQTT adapter (opt-in; RCS behaves exactly as before when disabled) ---
    mqtt_enabled: bool = False
    mqtt_host: str = "127.0.0.1"
    mqtt_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_client_id: str = "rcs-adapter"
    mqtt_keepalive: int = 60
    # Prefix prepended to every topic, useful for multi-tenant brokers.
    mqtt_topic_prefix: str = ""
    # Publish rate for device state. StateStream already caps at 10 Hz; this
    # allows further downsampling to relieve broker pressure. 0 disables state
    # publishing entirely.
    mqtt_state_publish_hz: float = 10.0
    # Reconnect backoff bounds (seconds).
    mqtt_reconnect_min_delay: float = 1.0
    mqtt_reconnect_max_delay: float = 30.0


settings = RCSSettings()
