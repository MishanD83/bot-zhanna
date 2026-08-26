from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Конфигурация приложения из переменных окружения."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==================================================
    # TELEGRAM
    # ==================================================

    bot_token: SecretStr = Field(
        ...,
        description="Токен Telegram-бота",
    )

    zhanna_telegram_id: int = Field(
        ...,
        description="Telegram ID Жанны для уведомлений",
    )

    # ==================================================
    # APPLICATION
    # ==================================================

    app_env: str = Field(
        default="development",
        description="Окружение: development | production",
    )

    log_level: str = Field(
        default="INFO",
        description="Уровень логирования",
    )

    # ==================================================
    # GOOGLE SHEETS
    # ==================================================

    google_credentials_file: Path = Field(
        default=BASE_DIR
        / "credentials"
        / "service_account.json",
        description=(
            "Путь к JSON-ключу "
            "сервисного аккаунта Google"
        ),
    )

    google_spreadsheet_id: str = Field(
        default="",
        description=(
            "ID Google-таблицы "
            "для работы с данными"
        ),
    )

    # ==================================================
    # PROPERTIES
    # ==================================================

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


settings = Settings()