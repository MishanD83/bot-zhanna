from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.setup import setup_dispatcher


def create_bot(token: str) -> Bot:
    """Создаёт экземпляр Telegram-бота."""
    return Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Создаёт и настраивает диспетчер aiogram."""
    dispatcher = Dispatcher(storage=MemoryStorage())
    setup_dispatcher(dispatcher)
    return dispatcher
