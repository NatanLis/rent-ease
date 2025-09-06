from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "Rent ease API"
    DATABASE_URL: str = 'postgresql+asyncpg://root:pass@127.0.0.1:5432/rentease_db_dev'
    DEBUG: bool = True

    # JWT Settings
    JWT_SECRET: str = 'b200e58d66b754c70d26dd488a2bce1e3d5ae5a64dfc80013948ea7199574a11' # Change in production
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 30  # minutes

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
