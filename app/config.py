import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    value = value.strip()
    return value or None


@dataclass(frozen=True)
class Settings:
    slack_bot_token: str | None = _env("SLACK_BOT_TOKEN")
    slack_signing_secret: str | None = _env("SLACK_SIGNING_SECRET")
    port: int = int(_env("PORT", "8000") or "8000")
    log_level: str = _env("LOG_LEVEL", "INFO") or "INFO"


settings = Settings()
