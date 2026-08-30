from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Robot Logic System"
    database_url: str = "sqlite+aiosqlite:///./data/prototype.db"
    log_level: str = "INFO"
    cloud_endpoint: str = "http://localhost:8080"
    use_cloud: bool = False

    # Optional API hardening. Disabled by default for ergonomic local dev.
    api_auth_enabled: bool = False
    api_keys: str = ""
    rate_limit_max: int = 120
    rate_limit_window_seconds: float = 60.0

    # RCS topology. When embedded (default) the RCS router is mounted on this
    # app under /api/rcs and its control loop shares this process' lifespan.
    # When disabled, RCS must be deployed separately and reached at
    # rcs_service_url (the frontend proxies /api/rcs there).
    rcs_embedded: bool = True
    rcs_service_url: str = "http://127.0.0.1:8100"

    # MQTT bridge to Mosquitto (shared with RCS / robot-app).
    # Disabled by default — most dev environments don't run a broker.
    sim_mqtt_enabled: bool = False
    sim_mqtt_host: str = "127.0.0.1"
    sim_mqtt_port: int = 1883

    class Config:
        env_file = ".env"


settings = Settings()
