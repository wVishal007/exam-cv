import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    GOOGLE_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""

    DATABASE_URL: str = "sqlite:///resume_agent.db"
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# LangChain LLM providers read API keys from os.environ, so mirror the
# centralized settings into the process environment exactly like the old
# scattered load_dotenv() calls did.
for _key in (
    "GOOGLE_API_KEY",
    "MISTRAL_API_KEY",
    "NVIDIA_API_KEY",
    "JWT_SECRET_KEY",
):
    _value = getattr(settings, _key)
    if _value:
        os.environ.setdefault(_key, _value)