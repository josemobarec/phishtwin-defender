from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PhishTwin Defender API"
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(default="postgresql+psycopg://postgres:postgres@db:5432/phishtwin")
    redis_url: str = Field(default="redis://redis:6379/0")

    upload_dir: str = Field(default="/tmp/phishtwin/uploads")
    sample_storage_dir: str = Field(default="/tmp/phishtwin/samples")

    jwt_secret: str = Field(default="change-me")
    default_demo_user: str = Field(default="analyst@phishtwin.local")

    llm_provider: str = Field(default="disabled")
    llm_model: str = Field(default="disabled")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
