from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.constants.buttons import START_BUTTON
from app.keyboards.callback_data import OnboardingCallback


def get_welcome_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура экрана приветствия."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=START_BUTTON,
                    callback_data=OnboardingCallback(action="start").pack(),
                ),
            ],
        ],
    )
