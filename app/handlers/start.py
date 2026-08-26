from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from app.keyboards.onboarding import get_welcome_keyboard
from app.messages.welcome import WELCOME_MESSAGE, WELCOME_PHOTO
from app.states.onboarding import TRAFFIC_SOURCE_KEY
from app.utils.traffic_source import parse_traffic_source


router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    command: CommandObject,
    state: FSMContext,
) -> None:
    """Обработчик команды /start — экран приветствия."""

    source = parse_traffic_source(command.args)

    await state.update_data(
        **{
            TRAFFIC_SOURCE_KEY: source.value
        }
    )

    await message.answer_photo(
        photo=FSInputFile(WELCOME_PHOTO),
        caption=WELCOME_MESSAGE,
        reply_markup=get_welcome_keyboard(),
    )