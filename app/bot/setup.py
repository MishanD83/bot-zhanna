from aiogram import Dispatcher

from app.handlers.router import main_router


def setup_dispatcher(dispatcher: Dispatcher) -> None:
    """Регистрирует роутеры, middleware и прочие зависимости диспетчера."""
    dispatcher.include_router(main_router)

    # TODO: зарегистрировать middleware при необходимости
    # TODO: внедрить сервисы (Google Sheets и др.) через workflow_data
