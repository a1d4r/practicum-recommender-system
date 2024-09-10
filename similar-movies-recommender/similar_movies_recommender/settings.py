from pathlib import Path

import tenacity

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from tenacity import wait_random_exponential

PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Настройки приложения."""

    # General
    state_file_path: Path = PROJECT_ROOT / "state.json"
    log_level: str = "INFO"
    run_interval_seconds: int = 60

    # Database
    postgres_dsn: PostgresDsn
    elasticsearch_host: str

    # Elasticsearch
    movies_index: str = "movies"

    # Retries
    retry_max_delay: float = 60.0  # in seconds
    retry_min_delay: float = 1.0  # in seconds
    retry_multiplier: float = 2

    ttl: int = 300

    @property
    def retry_policy(self) -> wait_random_exponential:
        """Randomly wait up to `retry_multiplier`^x * `retry_min_delay` seconds
        between each retry until the range reaches retry_max_delay seconds,
        then randomly up to `retry_max_delay` seconds afterwards.
        """
        return tenacity.wait_random_exponential(
            multiplier=self.retry_multiplier, min=self.retry_min_delay, max=self.retry_max_delay
        )


settings = Settings(_env_file=PROJECT_ROOT / ".env")
