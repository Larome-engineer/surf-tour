from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from bot.filters.isAdmin import IsAdmin
from bot.handlers.handler_utils import clear_and_delete, send_big_message, answer_and_delete
from bot.keyboards.admin import *
from database import service

admin_direct = Router()

headerAdd = "<b>➕ СОЗДАНИЕ НАПРАВЛЕНИЯ ➕</b>"
headerRemove = "<b>🗑 УДАЛЕНИЕ НАПРАВЛЕНИЯ 🗑</b>"
headerMenu = "<b>🗺 МЕНЮ НАПРАВЛЕНИЙ 🗺</b>"
directList = "<b>📋 СПИСОК НАПРАВЛЕНИЙ 📋</b>"


# --------------------
# ADD DIRECTION
# --------------------
class AddDirection(StatesGroup):
    direction = State()


@admin_direct.callback_query(F.data == "AddDirection", IsAdmin())
async def add_direction_start(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    await event.message.answer(
        text=f"{headerAdd}\n• Отправьте направление",
        reply_markup=await back_to("Отменить", "BackToDirectionsMenu")
    )
    await state.set_state(AddDirection.direction)


@admin_direct.message(AddDirection.direction, IsAdmin())
async def add_direction(event: Message, state: FSMContext):
    direction = await service.create_destination(event.text)
    if direction:
        await event.answer(
            text=f"{headerAdd}\n• Направление успешно создано!",
            reply_markup=await direct_menu()
        )
    else:
        await event.answer(
            text=f"{headerAdd}\n• При создании направления что-то пошло не так\nПопробуйте еще раз",
            reply_markup=await direct_menu()
        )
    await state.clear()


# --------------------
# DELETE DIRECTION
# --------------------
class DeleteDirection(StatesGroup):
    directions = State()
    dir_name = State()


@admin_direct.callback_query(F.data == "DeleteDirection", IsAdmin())
async def delete_direction_start(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    directions = await service.get_all_destinations()
    if directions:
        await state.update_data(directions=directions)
        await event.message.answer(
            text=f"{headerRemove}\n\n<b>ВНИМАНИЕ!</b> При удалении направления, "
                 "удалятся ВСЕ туры и УРОКИ по этому направлению! "
                 "Хотите продолжить?",
            reply_markup=apply_delete_dir().as_markup()
        )
        await state.set_state(DeleteDirection.directions)
    else:
        await event.message.answer(
            text=f"{headerRemove}\n• Пока не существует ни одного направления",
            reply_markup=await direct_menu()
        )


@admin_direct.callback_query(F.data.startswith("DeleteDir_"), DeleteDirection.directions, IsAdmin())
async def delete_direction_apply(event: CallbackQuery, state: FSMContext):
    await answer_and_delete(event)
    call = event.data.split("_")[1]
    if call == 'decline':
        await state.clear()
        await event.message.answer(
            text=headerMenu,
            reply_markup=await direct_menu()
        )
        return

    elif call == "apply":
        data = await state.get_data()
        directions = data['directions']
        await event.message.answer(
            text=f"{headerRemove}\n• Выберите направление для удаления",
            reply_markup=await simple_build_dynamic_keyboard(
                list_of_values=directions,
                value_key="name",
                callback="DirectionDelete_",
                back_callback="BackToDirectionsMenu",
                back_text="🔙"
            )
        )
        await state.set_state(DeleteDirection.dir_name)


@admin_direct.callback_query(F.data.startswith("DirectionDelete_"), DeleteDirection.dir_name, IsAdmin())
async def delete_direction_choice(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    direction = event.data.split("_")[1]
    has_booked = await service.has_future_bookings_for_destination(direction)

    if has_booked is None or not direction:
        await event.message.answer(
            text=f"{headerRemove}\n• При удалении направления {direction} возникла ошибка",
            reply_markup=await direct_menu()
        )
        return

    if has_booked:
        await event.message.answer(
            text=f"{headerRemove}\n• Нельзя удалить направление, пока по нему существуют предстоящие туры или уроки",
            reply_markup=await direct_menu()
        )
        return

    deleted = await service.delete_destination_by_name(direction)
    if deleted:
        await event.message.answer(
            text=f"{headerRemove}\n• Направление {direction} успешно удалено",
            reply_markup=await direct_menu()
        )

    else:
        await event.message.answer(
            text=f"{headerRemove}\n• При удалении направления {direction} возникла ошибка",
            reply_markup=await direct_menu()
        )


# --------------------
# GET DIRECTION
# --------------------
@admin_direct.callback_query(F.data == "DirectionsList", IsAdmin())
async def directions_list(event: CallbackQuery, state: FSMContext):
    await clear_and_delete(event, state)
    directions = await service.get_all_destinations()

    if directions:
        lines = [f"{directList}"]
        for i, direct in enumerate(directions, start=1):
            lines.append(f"{i}. {direct['name']}")
        text = "\n".join(lines)

        await send_big_message(
            event.message,
            text,
            reply_markup=await direct_menu()
        )
    else:
        await event.message.answer(
            text=f"{directList}\n• Пока нет ни одного доступного направления",
            reply_markup=await direct_menu()
        )
