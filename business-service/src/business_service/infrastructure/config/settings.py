from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    business_database_url: str = "postgresql+psycopg://business_user:change_me@localhost:5432/business_db"
    jwt_public_key: str | None = None
    jwt_public_key_path: str | None = None
    jwt_issuer: str = "engine-repair-auth"
    jwt_audience: str = "engine-repair-api"
    jwt_allowed_algorithm: str = "RS256"
    cors_origins: str = "http://localhost:5173"

    @model_validator(mode="after")
    def _check_algorithm(self) -> "Settings":
        # Only asymmetric RS256 is accepted; a symmetric or "none" setting would weaken verification.
        if self.jwt_allowed_algorithm != "RS256":
            raise ValueError("JWT_ALLOWED_ALGORITHM must be RS256")
        return self

    @property
    def database_url(self) -> str:
        # Accept plain postgresql:// URLs and select the psycopg 3 driver.
        url = self.business_database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    def load_public_key(self) -> str:
        if bool(self.jwt_public_key) == bool(self.jwt_public_key_path):
            raise ValueError("Set exactly one of JWT_PUBLIC_KEY or JWT_PUBLIC_KEY_PATH")
        if self.jwt_public_key:
            return self.jwt_public_key.replace("\\n", "\n")
        return Path(self.jwt_public_key_path or "").read_text(encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
