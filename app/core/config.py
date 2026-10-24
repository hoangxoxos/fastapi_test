from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str
    algorithm: str = "HS256"
    expires_in_minutes: int = 15
    expires_in_days: int = 7
    access_key: str
    log_level: str = "INFO"


settings = Settings()
