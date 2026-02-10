from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "BioStage"
    environment: str = "development"
    debug: bool = True

    database_url: str = "sqlite+aiosqlite:///./biostage.db"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120
    admin_username: str = "admin"
    admin_password_hash: str = "$2b$12$hJ3T9Kn3bSLIivN0rL9hiOxXxTWlyfrf5SUf8x8z39SmqQfr6s27q"  # admin123

    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""
    telegram_parse_mode: str = "HTML"


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
