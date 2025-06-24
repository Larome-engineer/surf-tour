import database.repository as repo
from utils import date_utils


# Добавить направление
async def create_destination(destination: str):
    try:
        await repo.create_destination(destination)
        return True
    except Exception as ex:
        pass


# Добавить тур
async def create_tour(name, desc, places, start, end, price, destination):
    try:
        await repo.create_tour(name, desc, places, start, end, int(price), destination)
        return True
    except Exception as ex:
        pass


# Создать пользователя
async def create_user(tg_id, username, email, phone):
    try:
        await repo.create_user(tg_id, username, email, phone)
        return True
    except Exception as ex:
        pass


# Создать платеж
async def create_payment(date, price, user, tour):
    try:
        await repo.create_payment(date, price, user, tour)
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
        all_dest = await repo.get_all_dest()
        if all_dest is None or len(all_dest) == 0:
            return None
        return all_dest
    except Exception as ex:
        pass


# Получить список всех туров направлений
async def get_all_tours() -> list | None:
    try:
        all_tours = await repo.get_all_tours()
        if all_tours is None or len(all_tours) == 0:
            return None
        tours = []
        for t in all_tours:
            tour = {
                'Название': t.tour_name,
                'Направление': t.tour_destination.destination,
                'Описание': t.tour_desc,
                'Места': t.tour_places,
                'Даты': date_utils.format_date_range(t.start_date, t.end_date),
                'Цена': f"{float(t.tour_price)}₽"
            }
            tours.append(tour)
        return tours
    except Exception as ex:
        pass

async def get_tour_by_name(tour_name):
    try:
        tour = await repo.get_tour_by_name(tour_name)
        if tour is None:
            return None
        return {
                'Название': tour.tour_name,
                'Направление': tour.tour_destination.destination,
                'Описание': tour.tour_desc,
                'Места': tour.tour_places,
                'Даты': date_utils.format_date_range(tour.start_date, tour.end_date),
                'Цена': f"{float(tour.tour_price)}₽"
            }
    except Exception as ex:
        return None

# Получить список туров по направлению
async def get_all_tour_by_dest(destination_name):
    try:
        tour_list = await repo.get_all_tour_by_dest(destination_name)
        if tour_list is None or len(tour_list) == 0:
            return None
        tours = []
        for t in tour_list:
            tour = {
                'Название': t.tour_name,
                'Направление': t.tour_destination.destination,
                'Описание': t.tour_desc,
                'Места': t.tour_places,
                'Даты': date_utils.format_date_range(t.start_date, t.end_date),
                'Цена': f"{float(t.tour_price)}₽"
            }
            tours.append(tour)
        return tours
    except Exception as ex:
        pass


# Получить список свободных туров по направлению
async def get_all_free_tour_by_dest(destination_name):
    try:
        free_tours = await repo.get_all_free_tour_by_dest(destination_name)
        if free_tours is None or len(free_tours) == 0:
            return None
        return free_tours
    except Exception as ex:
        pass


# Получить информацию пользователя по телефону или Email
async def get_user_by_phone_or_email(email_or_phone: str):
    try:
        if "@" in email_or_phone:
            user = await repo.get_user_by_email(email=email_or_phone)
            if user is None:
                return None
            return {
                'id': user.user_tg_id,
                'name': user.user_name,
                'phone': user.user_phone,
                'email': user.user_email,
                'tours': [t.tour.tour_name for t in user.tours]
            }

        elif email_or_phone.replace("+", "").isdigit():
            user = await repo.get_user_by_phone(phone=email_or_phone)
            if user is None:
                return None
            return {
                'id': user.user_tg_id,
                'name': user.user_name,
                'phone': user.user_phone,
                'email': user.user_email,
                'tours': [t.tour.tour_name for t in user.tours]
            }

    except Exception as ex:
        return None


# Получить список пользователей на конкретный тур
async def get_users_by_tour(tour_name: str):
    try:
        user_by_tour = await repo.get_users_by_tour(tour_name)
        if user_by_tour is None:
            return None
        return user_by_tour
    except Exception as ex:
        pass


# Получить список всех пользователей
async def get_all_users():
    try:
        users = await repo.get_all_users()
        if users is None or len(users) == 0:
            return None
        users = []
        for u in users:
            user = {
                "Имя": u['user_name'],
                "Telegram ID": u['user_tg_id'],
                "Телефон": u['user_phone'],
                "Email": u['user_email']
            }
            users.append(user)
        return users
    except Exception as ex:
        pass

async def get_user_by_tg_id(tg_id):
    try:
        user = await repo.get_user_by_tg_id(tg_id)
        if user is None:
            return None
        return {
            'id': user.user_tg_id,
            'name': user.user_name,
            'phone': user.user_phone,
            'email': user.user_email,
            'tours': [t.tour.tour_name for t in user.tours]
        }

    except Exception as ex:
        pass

async def get_all_users_ids():
    try:
        users = await repo.get_all_users_ids()
        if users is None or len(users) == 0:
            return None
        return users
    except Exception as ex:
        pass


# Получить список всех оплаченывх туров
async def get_all_booked_tours():
    try:
        booked_tours = await repo.get_all_booked_tours()
        if booked_tours is None:
            return None
        tours = []
        for payment in booked_tours:
            pay = {
                "Пользователь": f"{payment.user.user_email} ({payment.user.user_tg_id})",
                "Тур": f"{payment.tour.tour_name}",
                "Цена": f"{payment.tour.tour_price}"
            }
            tours.append(pay)
    except Exception as ex:
        pass


# Получить кол-во мест на тур
async def get_places_by_tour(tour_name):
    try:
        places = await repo.get_places_by_tour(tour_name)
        if places is None or len(places) == 0:
            return None
        return places
    except Exception as ex:
        pass


# Получить тур по дате начала
async def get_tours_by_start_date(date):
    try:
        tours = await repo.get_tours_by_start_date(date)
        if tours is None or len(tours) == 0:
            return None
        return tours
    except Exception as ex:
        pass


# Получить тур в диапазоне дат
async def get_tours_by_dates_between(date_1, date_2):
    try:
        tours = await repo.get_tours_by_dates_between(date_1, date_2)
        if tours is None or len(tours) == 0:
            return None
        return tours
    except Exception as ex:
        pass


# Добавить мест на тур
async def add_places_on_tour(tour_name, num_of_places: int):
    try:
        await repo.add_places_on_tour(tour_name, num_of_places)
        return True
    except Exception as ex:
        pass


# Удалить тур
async def delete_tour(tour_name: str):
    try:
        await repo.delete_tour(tour_name)
        return True
    except Exception as ex:
        pass


# Удалить направление
async def delete_dest(dest_name: str):
    try:
        await repo.delete_dest(dest_name)
        return True
    except Exception as ex:
        pass
