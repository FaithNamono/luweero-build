from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from environment variables / .env (no hardcoded secrets)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./luweero_build.db"

    storage_endpoint_url: str = ""
    storage_region: str = "eu-west-1"
    storage_bucket: str = "engineering-blueprints"
    storage_access_key_id: str = ""
    storage_secret_access_key: str = ""
    storage_public_base_url: str = ""
    storage_use_signed_urls: bool = False
    storage_signed_url_ttl_seconds: int = 900

    # If set, the webhook requires a matching X-Webhook-Secret header.
    webhook_shared_secret: str = ""

    laboremus_api_key: str = ""
    verify_ug_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
