from database.repository import *


# Добавить направление
async def create_destination(destination: str):
    try:
        await create_destination(destination)
        return True
    except Exception as ex:
        pass


# Добавить тур
async def create_tour(name, desc, places, start, end, price, destination):
    try:
        await create_tour(name, desc, places, start, end, price, destination)
        return True
    except Exception as ex:
        pass


# Создать пользователя
async def create_user(tg_id, username, email, phone):
    try:
        await create_user(tg_id, username, email, phone)
        return True
    except Exception as ex:
        pass


# Создать платеж
async def create_payment(date, price, user, tour):
    try:
        await create_payment(date, price, user, tour)
        return True
    except Exception as e:
        pass


# # Обновить тур
# async def update_tour(): pass
#
#
# # Обновить направление
# async def update_destination(): pass
#
#
# # Оббновить информацию о пользователе
# async def update_user(): pass


# Получить список доступных направлений
async def get_all_dest() -> list | None:
    try:
        all_dest = await get_all_dest()
        if all_dest is None:
            return None
        return all_dest
    except Exception as ex:
        pass


# Получить список туров по направлению
async def get_all_tour_by_dest(destination_name):
    try:
        tour_list = await get_all_tour_by_dest(destination_name)
        if tour_list is None:
            return None
        return tour_list
    except Exception as ex:
        pass


# Получить список свободных туров по направлению
async def get_all_free_tour_by_dest(destination_name):
    try:
        free_tours = await get_all_free_tour_by_dest(destination_name)
        if free_tours is None:
            return None
        return free_tours
    except Exception as ex:
        pass


# Получить информацию пользователя по телефону или Email
async def get_user_by_phone_or_email(email_or_phone: str):
    try:
        if "@" in email_or_phone:
            user = await get_user_by_email(email=email_or_phone)
            if user is None:
                return None
            return user

        elif email_or_phone.replace("+", "").isdigit():
            user = await get_user_by_phone(phone=email_or_phone)
            if user is None:
                return None
            return user

    except Exception as ex:
        pass


# Получить список пользователей на конкретный тур
async def get_users_by_tour(tour_name: str):
    try:
        user_by_tour = await get_users_by_tour(tour_name)
        if user_by_tour is None:
            return None
        return user_by_tour
    except Exception as ex:
        pass


# Получить список всех пользователей
async def get_all_users():
    try:
        users = await get_all_users()
        if users is None:
            return None
        return users
    except Exception as ex:
        pass


# Получить список всех оплаченывх туров
async def get_all_payments():
    try:
        payments = await get_all_payments()
        if payments is None:
            return None
        return payments
    except Exception as ex:
        pass


# Получить кол-во мест на тур
async def get_places_by_tour(tour_name):
    try:
        places = await get_places_by_tour(tour_name)
        if places is None:
            return None
        return places
    except Exception as ex:
        pass


# Получить тур по дате начала
async def get_tours_by_start_date(date):
    try:
        tours = await get_tours_by_start_date(date)
        if tours is None:
            return None
        return tours
    except Exception as ex:
        pass


# Получить тур в диапазоне дат
async def get_tours_by_dates_between(date_1, date_2):
    try:
        tours = await get_tours_by_dates_between(date_1, date_2)
        if tours is None:
            return None
        return tours
    except Exception as ex:
        pass


# Добавить мест на тур
async def add_places_on_tour(tour_name, num_of_places: int):
    try:
        await add_places_on_tour(tour_name, num_of_places)
        return True
    except Exception as ex:
        pass


# Удалить тур
async def delete_tour(tour_name: str):
    try:
        await delete_tour(tour_name)
        return True
    except Exception as ex:
        pass


# Удалить направление
async def delete_dest(dest_name: str):
    try:
        await delete_dest(dest_name)
        return True
    except Exception as ex:
        pass

