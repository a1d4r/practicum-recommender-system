from pathlib import Path
from pydantic_settings import BaseSettings

from utils.advlogger import CustomizeLogger
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    log_file_path: Path
    log_level: str
    log_format: str
    log_rotation: str
    log_retention: str
    logger: CustomizeLogger | None = None

    mongodb_uri: str
    md_db_host: str
    md_db_port: int
    md_db_name: str
    md_db_user: str
    md_db_pass: str

    pg_db_host: str
    pg_db_port: int
    pg_db_name: str
    pg_db_user: str
    pg_db_pass: str

    class Config:
        env_file = ".env"
        extra = "ignore"

    def setup(self):
        self.logger = CustomizeLogger.customize_logging(
            self.log_file_path,
            self.log_level,
            self.log_rotation,
            self.log_retention,
            self.log_format,
        )


@lru_cache(maxsize=None)
def get_settings():
    settings = Settings()
    settings.setup()
    return settings
