from models import *


# Добавить направление
async def create_destination(): pass


# Добавить тур
async def create_tour(): pass


# Создать пользователя
async def create_user(): pass


# Создать платеж
async def create_payment(): pass


# Обновить тур
async def update_tour(): pass


# Обновить направление
async def update_destination(): pass


# Оббновить информацию о пользователе
async def update_user(): pass


# Получить список доступных направлений
async def get_all_dest(): pass


# Получить список туров по направлению
async def get_all_tour_by_dest(destination_name): pass


# Получить список свободных туров по направлению
async def get_all_free_tour_by_dest(destination_name): pass


# Получить информацию пользователя по телефону или Email
async def get_user_by(user_phone_or_email: str): pass


# Получить список пользователей на конкретный тур
async def get_users_by_tour(tour_name: str): pass


# Получить список всех пользователей
async def get_all_users(): pass


# Получить список всех оплаченывх туров
async def get_all_payments(): pass


# Получить кол-во мест на тур
async def get_places_by_tour(tour_name): pass


# Получить тур по дате начала
async def get_tours_by_start_date(date): pass


# Получить тур в диапазоне дат
async def get_tours_by_dates_between(date_1, date_2): pass


# Добавить мест на тур
async def add_places_on_tour(num_of_places: int): pass

# Удалить тур
async def delete_tour(tour_name: str): pass

# Удалить направление
async def delete_dest(dest_name: str): pass
