import asyncio
import sys

from app.bot.factory import create_bot, create_dispatcher
from app.config.settings import settings
from app.utils.logging import setup_logging


async def run() -> None:
    """Точка запуска приложения."""
    setup_logging(level=settings.log_level)

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
