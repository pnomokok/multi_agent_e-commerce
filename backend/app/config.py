from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    gemini_api_key: str = ""
    database_url: str = "sqlite:///./eko.db"
    secret_key: str = "dev-secret"
    environment: str = "development"
    log_level: str = "INFO"

    # Gemini model selection
    gemini_model: str = "gemini-2.5-flash"

    # CORS — comma-separated origins, e.g. "http://localhost:3000,https://app.example.com"
    cors_origins: str = "*"


settings = Settings()
