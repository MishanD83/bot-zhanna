from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards.callback_data import QuestionCallback


def get_interest_keyboard(
    interest_key: str,
    selected: list[str] | None = None,
) -> InlineKeyboardMarkup:
    """
    Одна кнопка для одного интереса.
    Кнопка находится непосредственно под описанием интереса.
    """

    selected = selected or []

    titles = {
        "travel": "✈️ Путешествия",
        "income": "💰 Доход",
        "community": "🤝 Окружение",
        "growth": "🌱 Развитие",
    }

    title = titles[interest_key]

    if interest_key in selected:
        button_text = f"☑️ {title}"
    else:
        button_text = f"☐ {title}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=QuestionCallback(
                        action="interest",
                        value=interest_key,
                    ).pack(),
                )
            ]
        ]
    )


def get_done_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопка завершения выбора интересов.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Готово",
                    callback_data=QuestionCallback(
                        action="done",
                        value="done",
                    ).pack(),
                )
            ]
        ]
    )


def get_contact_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопка перехода в личный Telegram Жанны.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Написать Жанне",
                    url="https://t.me/ZhannaMishanina",
                )
            ]
        ]
    )