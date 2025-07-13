import logging

from database.models import User
from repository.user_repository import UserRepository
from utils.serializer import serialize_user

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo

    async def create_user(self, tg_id):
        await self.repo.create_user(User(user_tg_id=tg_id))
        logger.info("Добавился новый пользователь:  %s", tg_id)
        return True

    async def get_all_users(self):
        users = await self.repo.get_all_users()
        if not users:
            return None
        result = []
        for u in users:
            result.append(serialize_user(u))
        return result

    async def get_user_by_phone_or_email(self, phone_or_email):
        user = await self.repo.get_user_by_phone_or_email(phone_or_email)
        if not user:
            return None
        return serialize_user(user)

    async def get_user_by_tg_id(self, tg_id):
        user = await self.repo.get_user_by_tg_id(tg_id)
        if not user:
            return None
        return serialize_user(user)

    async def get_user(self, tg_id):
        user = await self.repo.get_user_by_tg_id(tg_id)
        if not user:
            return None
        return user

    async def update_user(self, tg_id, name=None, email=None, phone=None):
        updated = await self.repo.update_user(
            User(
                user_tg_id=tg_id,
                user_name=name,
                user_email=email,
                user_phone=phone
            )
        )
        logger.info("Пользователь %s обновил данные", tg_id)
        return updated

    async def delete_user_by_tg_id(self, tg_id):
        await self.repo.delete_user_by_tg_id(tg_id)
        logger.info("Удален пользователь:  %s", tg_id)
        return True

    async def get_all_users_ids(self):
        ids = await self.repo.get_all_users_ids()
        if not ids:
            return None
        return list(ids)

    async def disable_notifications(self, tg_id):
        disabled = await self.repo.disable_notifications(tg_id)
        return disabled
