import logging
from typing import Optional

from aiogram import exceptions
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyMarkupUnion, Message

from bot.create import surf_bot

logger = logging.getLogger(__name__)


async def edit_and_answer(event: CallbackQuery, text, reply_markup=None):
    await safe_answer(event)
    await safe_edit_text(event, text, reply_markup)


async def clear_and_edit(
        event: CallbackQuery,
        state: FSMContext = None,
        text: str = None,
        reply_markup: Optional[ReplyMarkupUnion] = None
):
    await safe_answer(event)
    if state:
        await state.clear()
    await safe_edit_text(event=event, text=text, reply_markup=reply_markup)


async def safe_edit_text(event: CallbackQuery, text, reply_markup=None):
    try:
        await event.message.edit_text(text=text, reply_markup=reply_markup)
    except exceptions.TelegramBadRequest as tg:
        if "message is not modified" in str(tg):
            pass
        if "query is too old" in str(tg) or "query ID is invalid" in str(tg):
            pass
        else:
            logger.error(tg)
    except Exception as e:
        logger.error(e)


async def safe_send(chat_id, text, reply_markup=None):
    try:
        await surf_bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup
        )
        return True
    except Exception as e:
        logger.error(e)
        return False


async def safe_send_all(text, users, reply_markup):
    send, not_send = 0, 0
    for user in users:
        # if isinstance(user['notification'], int) and user['notification'] == 1:
        #     was_send = await safe_send(user['tg_id'], text, reply_markup)
        #     if was_send:
        #         send += 1
        #     else:
        #         not_send += 1
        if isinstance(user['notification'], bool) and user['notification']:
            was_send = await safe_send(user['tg_id'], text, reply_markup)
            if was_send:
                send += 1
            else:
                not_send += 1
    return send, not_send


async def safe_send_copy(chat_id, from_chat, message):
    try:
        await surf_bot.copy_message(
            chat_id=chat_id,
            from_chat_id=from_chat,
            message_id=message
        )
        return True
    except Exception as e:
        logger.error(e)
        return False


async def safe_send_copy_all(from_chat, message, users):
    send, not_send = 0, 0
    for user_id in users:
        was_send = await safe_send_copy(user_id, from_chat, message)
        if was_send:
            send += 1
        else:
            not_send += 1
    return send, not_send

async def safe_send_document(chat_id, document):
    try:
        await surf_bot.send_document(chat_id, document)
    except Exception as e:
        logger.error(e)

async def safe_answer(event):
    try:
        await event.answer()
    except exceptions.TelegramBadRequest as e:
        if "query is too old" in str(e):
            pass
        else:
            logger.error(e)

    except Exception as e:
        logger.error(e)


async def safe_delete(event: Message | CallbackQuery):
    try:
        await event.message.delete()
    except exceptions.TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            pass
        else:
            logger.error(e)

    except Exception as e:
        logger.error(e)


async def send_by_instance(event: Message | CallbackQuery, text: str, reply_markup=None):
    if isinstance(event, Message):
        await event.answer(text, reply_markup=reply_markup)
    else:
        await safe_answer(event)
        await safe_edit_text(event, text, reply_markup=reply_markup)


async def send_big_message(message, text, reply_markup=None):
    try:
        parts = [text[i:i + 4096] for i in range(0, len(text), 4096)]
        for idx, part in enumerate(parts):
            await message.answer(
                part,
                reply_markup=reply_markup if idx == len(parts) - 1 else None
            )
    except Exception as e:
        logger.error(e)


async def get_and_clear(state: FSMContext):
    try:
        data = await state.get_data()
        await state.clear()
        return data
    except Exception as e:
        logger.error(e)
