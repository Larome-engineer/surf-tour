from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


async def clear_and_delete(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()


async def answer_and_delete(event: CallbackQuery):
    await event.answer()
    await event.message.delete()

MAX_MESSAGE_LENGTH = 4096

async def send_big_message(message, text, reply_markup=None):
    """
    Универсальная функция отправки длинного текста частями.
    """
    parts = [text[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]
    for idx, part in enumerate(parts):
        await message.answer(
            part,
            reply_markup=reply_markup if idx == len(parts) - 1 else None
        )
