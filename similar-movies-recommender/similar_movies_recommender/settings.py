from pathlib import Path

from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Настройки приложения."""

    elasticsearch_host: str
    movies_index: str = "movies"


settings = Settings(_env_file=PROJECT_ROOT / ".env")
