import service
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.keyboards.user import *


user = Router()

@user.message(CommandStart())
async def start(event: Message, state: FSMContext):
    await state.clear()
    await event.answer("Добро пожаловать!", reply_markup=user_main_menu().as_markup())

@user.callback_query(F.data == "usertourlist")
async def tours_list(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await event.answer()
    await event.message.delete()
    tours = await service.get_all_tours()
    if tours is not None:
        result = ["📋 <b>Список всех туров:</b>\n"]
        for i, tour in enumerate(tours, start=1):
            result.append(
                f"<b>#{i}. <code>{tour['Название']}</code></b>\n"
                f"🔜 {tour['Направление']}\n"
                f"👥 Места: {tour['Места']}\n"
                f"📅 {tour['Даты']}\n"
            )
        await event.message.answer(f"{"\n".join(result)}", reply_markup=tour_menu().as_markup())
    else:
        await event.message.answer(f"<b>Пока нет туров</b>", reply_markup=tour_menu().as_markup())