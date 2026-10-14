import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config.settings import settings
from app.services.google_sheets.client import GoogleSheetsClient

from app.keyboards.callback_data import (
    OnboardingCallback,
    QuestionCallback,
)

from app.keyboards.questions import (
    get_interest_keyboard,
    get_done_keyboard,
    get_contact_keyboard,
)

from app.messages.questions import (
    FINAL_MESSAGE,
    INTERESTS,
    NAME_QUESTION,
    INTEREST_QUESTION,
)

from app.states.onboarding import (
    OnboardingStates,
    TRAFFIC_SOURCE_KEY,
)


router = Router(name="onboarding")
logger = logging.getLogger(__name__)


# ==================================================
# КНОПКА «НАЧАТЬ»
# ==================================================

@router.callback_query(
    OnboardingCallback.filter(F.action == "start")
)
async def on_start_button(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    await state.set_state(
        OnboardingStates.waiting_name
    )

    await callback.message.answer(
        "😊 Рада знакомству!\n\n"
        "Как мне к тебе обращаться?"
    )

    await callback.answer()


# ==================================================
# ПОЛУЧЕНИЕ ИМЕНИ
# ==================================================

@router.message(
    OnboardingStates.waiting_name
)
async def process_name(
    message: Message,
    state: FSMContext,
) -> None:

    name = (message.text or "").strip()

    if not name:
        await message.answer(
            "Пожалуйста, напиши своё имя."
        )
        return

    await state.update_data(
        name=name
    )

    await state.set_state(
        OnboardingStates.waiting_country
    )

    await message.answer(
        NAME_QUESTION.format(
            name=name
        )
    )


# ==================================================
# ПОЛУЧЕНИЕ СТРАНЫ
# ==================================================

@router.message(
    OnboardingStates.waiting_country
)
async def process_country(
    message: Message,
    state: FSMContext,
) -> None:

    country = (message.text or "").strip()

    if not country:
        await message.answer(
            "Пожалуйста, напиши страну, где ты сейчас живёшь."
        )
        return

    await state.update_data(
        country=country
    )

    await state.update_data(
        interests=[]
    )

    await state.set_state(
        OnboardingStates.choosing_interests
    )

    await message.answer(
        INTEREST_QUESTION
    )

    await message.answer(
        INTERESTS["travel"],
        reply_markup=get_interest_keyboard(
            "travel",
            [],
        ),
    )

    await message.answer(
        INTERESTS["income"],
        reply_markup=get_interest_keyboard(
            "income",
            [],
        ),
    )

    await message.answer(
        INTERESTS["community"],
        reply_markup=get_interest_keyboard(
            "community",
            [],
        ),
    )

    await message.answer(
        INTERESTS["growth"],
        reply_markup=get_interest_keyboard(
            "growth",
            [],
        ),
    )

    await message.answer(
        "Когда выберешь всё необходимое, нажми:",
        reply_markup=get_done_keyboard(),
    )


# ==================================================
# ВЫБОР ИНТЕРЕСА
# ==================================================

@router.callback_query(
    OnboardingStates.choosing_interests,
    QuestionCallback.filter(
        F.action == "interest"
    ),
)
async def process_interest(
    callback: CallbackQuery,
    callback_data: QuestionCallback,
    state: FSMContext,
) -> None:

    data = await state.get_data()

    if data.get("submission_complete"):
        await callback.answer("Заявка уже отправлена.", show_alert=True)
        return

    if data.get("submission_in_progress"):
        await callback.answer("Заявка уже обрабатывается.", show_alert=True)
        return

    selected = list(
        data.get("interests", [])
    )

    interest = callback_data.value

    if interest in selected:
        selected.remove(interest)
    else:
        selected.append(interest)

    await state.update_data(
        interests=selected
    )

    await callback.message.edit_reply_markup(
        reply_markup=get_interest_keyboard(
            interest,
            selected,
        )
    )

    await callback.answer()


# ==================================================
# КНОПКА «ГОТОВО»
# ==================================================

@router.callback_query(
    OnboardingStates.choosing_interests,
    QuestionCallback.filter(
        F.action == "done"
    ),
)
async def process_interests_done(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    data = await state.get_data()

    if data.get("submission_complete"):
        await callback.answer("Заявка уже отправлена.", show_alert=True)
        return

    if data.get("submission_in_progress"):
        await callback.answer("Заявка уже обрабатывается.", show_alert=True)
        return

    selected = data.get(
        "interests",
        [],
    )

    if not selected:
        await callback.answer(
            "Выбери хотя бы один вариант.",
            show_alert=True,
        )
        return

    interest_text = "\n".join(
        f"• {INTERESTS[key]}"
        for key in selected
    )

    await state.update_data(
        interest_text=interest_text
    )

    # ==================================================
    # ИСТОЧНИК
    # ==================================================

    source = data.get(
        TRAFFIC_SOURCE_KEY,
        "unknown",
    )

    # ==================================================
    # TELEGRAM КЛИЕНТА
    # ==================================================

    telegram_username = (
        f"@{callback.from_user.username}"
        if callback.from_user.username
        else ""
    )

    telegram_id = callback.from_user.id

    # ==================================================
    # GOOGLE SHEETS
    # ==================================================

    if not data.get("saved_to_sheets"):
        await state.update_data(submission_in_progress=True)
        client = GoogleSheetsClient(
            credentials_file=settings.google_credentials_file,
            spreadsheet_id=settings.google_spreadsheet_id,
            credentials_json=(
                settings.google_credentials_json.get_secret_value()
                if settings.google_credentials_json
                else None
            ),
        )

        try:
            await asyncio.to_thread(
                client.append_client,
                name=data.get("name", ""),
                country=data.get("country", ""),
                interests=interest_text,
                source=source,
                telegram_username=telegram_username,
                telegram_id=telegram_id,
            )
        except Exception as error:
            logger.error(
                "Could not save a registration to Google Sheets (%s)",
                type(error).__name__,
            )
            await state.update_data(submission_in_progress=False)
            await callback.message.answer(
                "Не удалось сохранить ответы. Попробуй нажать «✅ Готово» ещё раз."
            )
            await callback.answer()
            return

        await state.update_data(saved_to_sheets=True)

    # ==================================================
    # УВЕДОМЛЕНИЕ ЖАННЕ
    # ==================================================

    telegram_link = ""

    if telegram_username:
        telegram_link = (
            f"https://t.me/"
            f"{telegram_username.lstrip('@')}"
        )

    notification = (
        "🔔 <b>Новый контакт из бота Путешествия и возможности</b>\n\n"
        f"<b>Имя:</b> {data.get('name', '')}\n"
        f"<b>Страна:</b> {data.get('country', '')}\n"
        f"<b>Интересы:</b>\n"
        f"{interest_text}\n\n"
        f"<b>Источник:</b> {source}\n"
        f"<b>Telegram:</b> "
        f"{telegram_username or 'нет username'}\n"
        f"<b>Telegram ID:</b> {telegram_id}"
    )

    if telegram_link:
        notification += (
            f"\n\n"
            f"💬 <a href=\"{telegram_link}\">"
            f"Открыть Telegram"
            f"</a>"
        )

    if not data.get("notification_sent"):
        try:
            await callback.bot.send_message(
                chat_id=settings.zhanna_telegram_id,
                text=notification,
                parse_mode="HTML",
            )
        except Exception as error:
            logger.error(
                "Could not send the registration notification (%s)",
                type(error).__name__,
            )
            await state.update_data(submission_in_progress=False)
            await callback.message.answer(
                "Ответы сохранены, но уведомление Жанне временно не отправилось. "
                "Нажми «✅ Готово» ещё раз — повторю отправку без повторной записи."
            )
            await callback.answer()
            return

        await state.update_data(notification_sent=True)

    # ==================================================
    # СООБЩЕНИЕ КЛИЕНТУ
    # ==================================================

    try:
        await callback.message.answer(
            FINAL_MESSAGE,
            reply_markup=get_contact_keyboard(),
        )
    except Exception as error:
        logger.error(
            "Could not send the final registration message (%s)",
            type(error).__name__,
        )
        await state.update_data(submission_in_progress=False)
        await callback.answer()
        return

    await state.update_data(
        submission_in_progress=False,
        submission_complete=True,
    )

    await callback.answer()
