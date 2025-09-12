import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or defaults."""

    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_NAME: str = os.getenv("POSTGRES_NAME", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: int = os.getenv("POSTGRES_PORT", 5432)

    PROJECT_NAME: str = "Rent ease API"
    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
    DEBUG: bool = True

    JWT_SECRET: str = (
        "b200e58d66b754c70d26dd488a2bce1e3d5ae5a64dfc80013948ea7199574a11"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
