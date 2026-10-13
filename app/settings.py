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

    title: str = Field('FastAPI', validation_alias='APP_TITLE', description='The title of the FastAPI application.')
    version: str = Field('0.1.0', validation_alias='APP_VERSION', description='The version of the FastAPI application.')
    debug: bool = Field(False, validation_alias='APP_DEBUG', description='Enable or disable debug mode for the FastAPI application.')

    db_host: str = Field('localhost', validation_alias='APP_DB_HOST', description='The database host for the FastAPI application.')
    db_port: int = Field(default=3307, ge=1, le=65535, validation_alias='APP_DB_PORT', description='The database port for the FastAPI application.')
    db_user: str = Field('root', validation_alias='APP_DB_USER', description='The database user for the FastAPI application.')
    db_password: SecretStr = Field(default=SecretStr(""), validation_alias='APP_DB_PASSWORD', description='The database password for the FastAPI application.')
    db_name: str = Field('simple', validation_alias='APP_DB_NAME', description='The database name for the FastAPI application.')

    openai_api_key: SecretStr = Field(default=SecretStr(""), validation_alias="OPENAI_API_KEY", description='The OpenAI API key for the FastAPI application.')

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