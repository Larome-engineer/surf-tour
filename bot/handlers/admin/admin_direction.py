from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile
from dependency_injector.wiring import Provide, inject

from DIcontainer import Container
from bot.filters.isAdmin import IsAdmin
from bot.handlers.handler_utils import *
from bot.keyboards.admin import *
from service.booking_service import BookingService
from service.destination_service import DestService
from service.export_service import ExportService

admin_direct = Router()

ADD = "<b>➕ СОЗДАНИЕ НАПРАВЛЕНИЯ ➕</b>"
REMOVE = "<b>🗑 УДАЛЕНИЕ НАПРАВЛЕНИЯ 🗑</b>"
MENU = "<b>🗺 МЕНЮ НАПРАВЛЕНИЙ 🗺</b>"
LIST = "<b>📋 СПИСОК НАПРАВЛЕНИЙ 📋</b>"


# --------------------
# ADD DIRECTION
# --------------------
class AddDirection(StatesGroup):
    direction = State()


@admin_direct.callback_query(F.data == "AddDirection", IsAdmin())
async def add_direction_start(event: CallbackQuery, state: FSMContext):
    await clear_and_edit(
        event,
        text=f"{ADD}\n• Отправьте направление",
        reply_markup=back_to("Отменить", "BackToDirectionsMenu")
    )
    await state.set_state(AddDirection.direction)


@admin_direct.message(AddDirection.direction, IsAdmin())
@inject
async def add_direction(
        event: Message,
        state: FSMContext,
        dest_service=Provide[Container.destination_service]
):
    direction = await dest_service.create_destination(event.text)
    if direction:
        await event.answer(
            text=f"{ADD}\n• Направление успешно создано!",
            reply_markup=direct_menu()
        )
    else:
        await event.answer(
            text=f"{ADD}\n• При создании направления что-то пошло не так\nПопробуйте еще раз",
            reply_markup=direct_menu()
        )
    await state.clear()


# --------------------
# DELETE DIRECTION
# --------------------
class DeleteDirection(StatesGroup):
    directions = State()
    dir_name = State()


@admin_direct.callback_query(F.data == "DeleteDirection", IsAdmin())
@inject
async def delete_direction_start(
        event: CallbackQuery,
        state: FSMContext,
        dest_service: DestService = Provide[Container.destination_service]
):
    await state.clear()
    await safe_answer(event)
    directions = await dest_service.get_all_destinations()
    if directions:
        await state.update_data(directions=directions)
        await safe_edit_text(
            event,
            text=f"{REMOVE}\n\n<b>ВНИМАНИЕ!</b> При удалении направления, "
                 "удалятся ВСЕ туры и УРОКИ по этому направлению! "
                 "Хотите продолжить?",
            reply_markup=apply_delete_dir()
        )
        await state.set_state(DeleteDirection.directions)
    else:
        await safe_edit_text(
            event,
            text=f"{REMOVE}\n• Пока не существует ни одного направления",
            reply_markup=direct_menu()
        )


@admin_direct.callback_query(F.data.startswith("DeleteDir_"), DeleteDirection.directions, IsAdmin())
async def delete_direction_apply(event: CallbackQuery, state: FSMContext):
    await safe_answer(event)
    call = event.data.split("_")[1]
    if call == 'decline':
        await state.clear()
        await safe_edit_text(
            event,
            text=MENU,
            reply_markup=direct_menu()
        )
        return

    elif call == "apply":
        data = await state.get_data()
        directions = data['directions']
        await safe_edit_text(
            event,
            text=f"{REMOVE}\n• Выберите направление для удаления",
            reply_markup=simple_build_dynamic_keyboard(
                list_of_values=directions,
                value_key="name",
                callback="DirectionDelete_",
                back_callback="BackToDirectionsMenu",
                back_text="🔙"
            )
        )
        await state.set_state(DeleteDirection.dir_name)


@admin_direct.callback_query(F.data.startswith("DirectionDelete_"), DeleteDirection.dir_name, IsAdmin())
@inject
async def delete_direction_choice(
        event: CallbackQuery,
        state: FSMContext,
        booking_service: BookingService = Provide[Container.booking_service]
):
    await safe_answer(event)

    direction = event.data.split("_")[1]
    await state.update_data(direction=direction)

    has_booked = await booking_service.has_future_bookings_for_destination(direction)

    if has_booked is None or not direction:
        await safe_edit_text(
            event,
            text=f"{REMOVE}\n• При удалении направления {direction} возникла ошибка",
            reply_markup=direct_menu()
        )
        return

    if has_booked:
        await safe_edit_text(
            event,
            text=f"{REMOVE}\n• Нельзя удалить направление, пока по нему существуют предстоящие туры или уроки",
            reply_markup=direct_menu()
        )
        return

    await safe_edit_text(
        event,
        text=f"{REMOVE}\n• Желайте сделать экспорт базы данных перед удалением?",
        reply_markup=yes_or_not(
            text_yes="Да",
            callback_yes="ExportDataWhenRemove_yes",
            text_no="Нет",
            callback_no="ExportDataWhenRemove_no"
        )
    )


@admin_direct.callback_query(F.data.startswith("ExportDataWhenRemove_"), IsAdmin())
@inject
async def export_db(
        event: CallbackQuery,
        state: FSMContext,
        dest_service: DestService = Provide[Container.destination_service]
):
    data = await get_and_clear(state)
    await safe_answer(event)

    answer = event.data.split("_")[1]
    if answer == "yes":
        export = await ExportService.export_db()
        if not export:
            await safe_edit_text(
                event,
                "<b>💻 ГЛАВНОЕ МЕНЮ 💻</b>\n\nНаправление НЕ удалено!\nПроизошла ошибка при экспорте данных",
                reply_markup=main_menu()
            )
            return
        await safe_delete(event)
        filename = f"backup_{datetime.now().strftime('%d.%m.%Y | %H:%M:%S')}.xlsx"
        await event.message.answer_document(
            document=BufferedInputFile(export.read(), filename=filename),
            caption="📦 Бэкап данных."
        )

    deleted = await dest_service.delete_destination_by_name(data['direction'])
    if not deleted:
        if answer == 'yes':
            await event.message.answer(
                text=f"{REMOVE}\n• При удалении направления {data['direction']} возникла ошибка",
                reply_markup=main_menu()
            )
            return

        await safe_edit_text(
            event,
            text=f"{REMOVE}\n• При удалении направления {data['direction']} возникла ошибка",
            reply_markup=direct_menu()
        )
        return

    if answer == "yes":
        await event.message.answer(
            text=f"{REMOVE}\n• Направление {data['direction']} успешно удалено",
            reply_markup=direct_menu()
        )
        return

    await safe_edit_text(
        event,
        text=f"{REMOVE}\n• Направление {data['direction']} успешно удалено",
        reply_markup=direct_menu()
    )


# --------------------
# GET DIRECTION
# --------------------
@admin_direct.callback_query(F.data == "DirectionsList", IsAdmin())
@inject
async def directions_list(
        event: CallbackQuery,
        state: FSMContext,
        dest_service: DestService = Provide[Container.destination_service]
):
    await state.clear()
    await safe_answer(event)
    directions = await dest_service.get_all_destinations()

    if directions:
        lines = [f"{LIST}"]
        for i, direct in enumerate(directions, start=1):
            lines.append(f"{i}. {direct['name']}")
        text = "\n".join(lines)

        await safe_edit_text(
            event,
            text,
            reply_markup=direct_menu()
        )
    else:
        await safe_edit_text(
            event,
            text=f"{LIST}\n• Пока нет ни одного доступного направления",
            reply_markup=direct_menu()
        )
