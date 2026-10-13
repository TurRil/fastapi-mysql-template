import os
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

# --- ENV FILE LOADING ---
DEFAULT_ENV_FILES = [
    ".env",
    Path(__file__).resolve().parent.parent / ".env"
]

env_file = next((f for f in DEFAULT_ENV_FILES if os.path.exists(f)), None)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=env_file or Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    title: str = "FastAPI"
    version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = Field(default="/api", pattern=r"^/[^?#]*[^/?#]$")

    db_host: str = "localhost"
    db_port: int = Field(default=3307, ge=1, le=65535)
    db_user: str = "root"
    db_password: SecretStr = SecretStr("")
    db_name: str = "simple"

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="mysql+pymysql",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},
        )

    @property
    def env_file_path(self) -> Path:
        return Path(__file__).resolve().parent.parent / ".env"

settings = Settings()