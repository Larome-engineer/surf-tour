import service
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery


user = Router()

@user.message(CommandStart())
async def start(event: Message, state: FSMContext):
    await state.clear()
    await event.answer("Добро пожаловать!")

@user.callback_query(F.data == "destination")
async def get_destination(event: CallbackQuery, state: FSMContext):
    await state.clear()
    dest = await service.get_all_dest()
    if dest is None:
        await event.answer("Нет доступных направлений")
    else:
        await event.answer(f"Доступные направления: {dest}")

@user.callback_query(F.data == "tours_by_dest")
async def get_tours_by_dest(event: CallbackQuery, state: FSMContext):
    pass