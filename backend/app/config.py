from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    USE_MOCK_DATA: bool = True
    OPENAI_API_KEY: str | None = None
    # Future settings can be added here (e.g., GOOGLE_CALENDAR_CREDENTIALS)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
