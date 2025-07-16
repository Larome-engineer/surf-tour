import logging
from typing import Optional

from tortoise.expressions import Q

from database.models import User

logger = logging.getLogger(__name__)


class UserRepository:

    async def create_user(self, user: User) -> User:
        return await User.create(
            user_tg_id=user.user_tg_id,
            user_name=user.user_name,
            user_email=user.user_email,
            user_phone=user.user_phone
        )

    async def get_all_users(self) -> list[User]:
        return await User.all()

    async def get_user_by_tg_id(self, tg_id) -> Optional[User]:
        user = await User.filter(user_tg_id=tg_id).prefetch_related(
            "tours__tour",
            "surfs__surf",
            "tour_payments__tour",
            "surf_payments__surf"
        ).first()
        return user

    async def update_user(self, user_updated: User) -> bool:
        user = await User.get_or_none(user_tg_id=user_updated.user_tg_id)
        if user is not None:
            if user_updated.user_name is not None:
                user.user_name = user_updated.user_name
                await user.save(update_fields=["user_name"])
            if user_updated.user_email is not None:
                user.user_email = user_updated.user_email
                await user.save(update_fields=["user_email"])
            if user_updated.user_phone is not None:
                user.user_phone = user_updated.user_phone
                await user.save(update_fields=["user_phone"])
            return True
        else:
            return False

    async def get_user_by_phone_or_email(self, phone_or_email) -> Optional[User]:
        return await User.filter(
            Q(user_phone=phone_or_email) | Q(user_email=phone_or_email)
        ).first()

    async def delete_user_by_tg_id(self, tg_id) -> User | int:
        deleted = await User.filter(user_tg_id=tg_id).delete()
        return deleted

    async def get_all_users_ids(self) -> list[str]:
        return await User.all().values_list("user_tg_id", flat=True)

    async def disable_notifications(self, tg_id):
        user = await self.get_user_by_tg_id(tg_id)
        if not user: return False
        user.user_enable_notifications = False
        await user.save(update_fields=["user_enable_notifications"])
        return True
