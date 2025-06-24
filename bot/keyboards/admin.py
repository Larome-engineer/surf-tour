from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Туры и направления", callback_data='toursanddirections'),
        InlineKeyboardButton(text="Пользователи", callback_data='users'),
        width=1
    )


def tour_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Добавить тур", callback_data='addtour'),
        InlineKeyboardButton(text="Список туров", callback_data='tourlist'),
        InlineKeyboardButton(text="Тур по направлению", callback_data='tourbydirect'),
        InlineKeyboardButton(text="Удалить тур", callback_data="deletetour"),
        InlineKeyboardButton(text="Добавить мест на тур", callback_data='addtourplaces'),
        InlineKeyboardButton(text="Забронированные туры", callback_data='bookedtours'),
        InlineKeyboardButton(text="Назад", callback_data='backtotouranddirect'),
        width=1
    )


def direct_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Добавить направление", callback_data='adddirection'),
        InlineKeyboardButton(text="Доступные направления", callback_data='directionslist'),
        InlineKeyboardButton(text="Удалить направление", callback_data='deletedirection'),
        InlineKeyboardButton(text="Назад", callback_data='backtotouranddirect'),
        width=1
    )


def apply_delete_dir():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Да", callback_data='deletedir_apply'),
        InlineKeyboardButton(text="Отмена", callback_data='deletedir_decline'),
    )


def tour_and_directions():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Туры", callback_data='management_tour'),
        InlineKeyboardButton(text="Направления", callback_data='management_direct'),
        InlineKeyboardButton(text="Назад", callback_data='backtoadminmenu'),
        width=1
    )


###### USER ######
def user_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Рассылка", callback_data='usermailng'),
        InlineKeyboardButton(text="Список пользователей", callback_data='userslist'),
        InlineKeyboardButton(text="Информация о пользователе", callback_data='userinfo'),
        InlineKeyboardButton(text="Назад", callback_data='backtoadminmenu'),
        width=1
    )


def confirm_mailing():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Отправить", callback_data='send_mailing'),
        InlineKeyboardButton(text="Отмена", callback_data='decline_mailing')
    )


def user_info():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Telegram ID", callback_data='searchbytgid'),
        InlineKeyboardButton(text="Почта или номер телефона", callback_data='searchbyemailorphone'),
        InlineKeyboardButton(text="Назад", callback_data='backtousermenu'),
        width=1
    )
