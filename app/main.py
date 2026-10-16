import asyncio
import logging
import os
import sys

from app.bot.factory import create_bot, create_dispatcher
from app.config.settings import settings
from app.utils.logging import setup_logging


logger = logging.getLogger(__name__)


def log_google_configuration() -> None:
    """Report safe Google credential configuration facts for this process."""
    credentials_json = settings.google_credentials_json
    logger.info(
        "Google credentials configuration: env_present=%s env_length=%s "
        "settings_field_present=%s settings_is_none=%s settings_empty=%s "
        "settings_length=%s app_revision=%s deployment_id=%s",
        "GOOGLE_CREDENTIALS_JSON" in os.environ,
        len(os.environ.get("GOOGLE_CREDENTIALS_JSON", "")),
        hasattr(settings, "google_credentials_json"),
        credentials_json is None,
        credentials_json is not None and not credentials_json.get_secret_value(),
        len(credentials_json.get_secret_value()) if credentials_json is not None else None,
        os.getenv("RAILWAY_GIT_COMMIT_SHA") or os.getenv("GIT_COMMIT_SHA") or "unknown",
        os.getenv("RAILWAY_DEPLOYMENT_ID") or "unknown",
    )


async def run() -> None:
    """Точка запуска приложения."""
    setup_logging(level=settings.log_level)
    log_google_configuration()

    bot = create_bot(settings.bot_token.get_secret_value())
    dispatcher = create_dispatcher()

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


def main() -> None:
    """Синхронная обёртка для запуска через CLI."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run())


if __name__ == "__main__":
    main()
