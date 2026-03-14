from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    USE_MOCK_DATA: bool = True
    OPENAI_API_KEY: str | None = None
    NEXT_PUBLIC_APP_URL: str = "http://localhost:3000"
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    DATABASE_URL: str | None = None
    SESSION_SECRET: str = "super-secret-kairos-key"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
