import logging
from datetime import datetime

from database.models import SurfLesson
from repository.lesson_repository import LessonRepository
from service.destination_service import DestService
from utils.serializer import serialize_lesson, serialize_user

logger = logging.getLogger(__name__)


class LessonService:
    def __init__(self, lesson_repo: LessonRepository, destination_service: DestService):
        self.repo = lesson_repo
        self.dest_service = destination_service

    async def create_lesson(self, desc: str,
                            places: int,
                            start: datetime,
                            time: str,
                            duration: str,
                            price: float,
                            dest: str,
                            lesson_type: str
                            ):
        destination = await self.dest_service.get_destination(dest.lower())
        less_type = await self.repo.get_lesson_type(lesson_type.lower())
        if destination is None or less_type is None: return None
        unicode = await self.repo.create_lesson(
            SurfLesson(
                surf_desc=desc,
                surf_places=places,
                surf_duration=duration,
                start_date=start.date(),
                start_time=time,
                surf_price=price,
                surf_destination=destination,
                surf_type=less_type
            )
        )
        return True, unicode

    async def get_future_paid_lesson(self, code):
        lesson = await self.repo.get_future_paid_lesson(code)
        if not lesson:
            return None
        return serialize_lesson(surf=lesson)

    async def get_all_lessons(self):
        lessons = await self.repo.get_all_lessons()
        if not lessons:
            return None
        return [serialize_lesson(surf=l) for l in lessons]

    async def get_all_lessons_by_dest(self, destination_name: str):
        lessons = await self.repo.get_all_lessons_by_dest(destination_name.lower())
        if not lessons:
            return None
        return [serialize_lesson(surf=l) for l in lessons]

    async def get_all_lessons_with_places(self):
        lessons = await self.repo.get_all_lessons_with_places()
        if not lessons:
            return None
        return [serialize_lesson(surf=l) for l in lessons]

    async def get_lesson_by_code(self, code):
        lesson = await self.repo.get_lesson_by_code(code)
        if not lesson:
            return None
        return serialize_lesson(surf=lesson)

    async def get_lesson(self, code):
        lesson = await self.repo.get_lesson_by_code(code)
        if not lesson:
            return None
        return lesson

    async def get_booked_lesson_by_code(self, code):
        lesson = await self.repo.get_booked_lesson_by_code(code)
        if not lesson:
            return None
        users = []
        for user_surfs in lesson.user_surfs:
            if user_surfs.user:
                users.append(serialize_user(user_surfs.user))

        return serialize_lesson(surf=lesson, users=users)

    async def get_all_booked_lessons_future(self):
        lessons = await self.repo.get_all_booked_lessons_future()
        if not lessons:
            return None

        result = []
        for l in lessons:
            users = []
            for us in l.user_surfs:
                if us.user:
                    users.append(serialize_user(us.user))
            result.append(serialize_lesson(surf=l, users=users))
        return result

    async def reduce_places_on_lesson(self, code, count):
        result = await self.repo.reduce_places_on_lesson(code, count)
        if result is None:
            logger.exception(f"Тур '{code}' не найден.")
            return None
        if not result:
            logger.exception(f"Нельзя уменьшить места: недостаточно свободных мест в '{code}'.")
            return False
        return True

    async def add_places_on_lesson(self, code, count):
        result = await self.repo.add_places_on_lesson(code, count)
        if result is None:
            logger.exception(f"Тур '{code}' не найден.")
            return None
        return True

    async def delete_lesson(self, code):
        deleted = await self.repo.delete_lesson(code)
        if deleted == 0:
            logger.exception(f"Урок '{code}' не найден.")
            return None
        return True

    async def get_upcoming_user_lessons(self, tg_id):
        user_surfs = await self.repo.get_upcoming_user_lessons(tg_id)
        if not user_surfs:
            return None

        result = []
        for us in user_surfs:
            payment = await self.repo.get_user_lesson_payment(us.user_id, us.surf_id)
            result.append(serialize_lesson(surf=us.surf, payment=payment))
        return result

    async def get_lesson_types(self):
        types = await self.repo.get_lesson_types()
        if types is None: return None
        return types

    async def add_lesson_type(self, type_lesson):
        await self.repo.add_lesson_type(type_lesson)
        return True

    async def get_user_lesson_details(self, tg_id, code):
        us = await self.repo.get_user_lesson_details(tg_id, code)
        if not us:
            return None
        payment = await self.repo.get_user_lesson_payment(us.user_id, us.surf_id)
        return serialize_lesson(us.surf, payment)

    async def create_user_surf(self, user, surf):
        created = await self.repo.create_user_surf(user, surf)
        return created
