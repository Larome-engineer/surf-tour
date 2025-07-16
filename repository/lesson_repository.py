import logging
import uuid
from datetime import date
from typing import Optional

from database.models import LessonType, SurfLesson, UserSurf, SurfPayment
from utils.date_utils import safe_parse_date

logger = logging.getLogger(__name__)


class LessonRepository:
    """TYPE CREATE"""

    async def add_lesson_type(self, type_lesson: str) -> LessonType:
        return await LessonType.create(type=type_lesson.lower())

    """TYPE GET"""

    async def get_lesson_types(self) -> list[LessonType]:
        return await LessonType.all()

    async def get_lesson_type(self, lesson_type) -> LessonType:
        return await LessonType.get_or_none(type=lesson_type)

    """LESSON CREATE"""

    async def create_lesson(self, surf_lesson: SurfLesson) -> str:
        code = str(uuid.uuid4())
        await SurfLesson.create(
            unique_code=code,
            surf_desc=surf_lesson.surf_desc,
            surf_places=surf_lesson.surf_places,
            start_date=surf_lesson.start_date,
            start_time=surf_lesson.start_time,
            surf_duration=surf_lesson.surf_duration,
            surf_price=surf_lesson.surf_price,
            surf_destination=surf_lesson.surf_destination,
            surf_type=surf_lesson.surf_type
        )
        return code

    async def create_user_surf(self, user, surf) -> bool:
        exists = await UserSurf.filter(user=user, surf=surf).exists()
        if exists:
            return False
        await UserSurf.create(user=user, surf=surf)
        return True

    """LESSON GET"""

    async def get_all_lessons(self) -> list[SurfLesson]:
        return await (
            SurfLesson.all()
            .prefetch_related("surf_destination", "surf_type")
            .order_by("start_date")
        )

    async def get_all_lessons_with_places(self) -> list[SurfLesson]:
        return await (
            SurfLesson.filter(surf_places__gt=0)
            .prefetch_related("surf_destination", "surf_type")
            .order_by("start_date")
        )

    async def get_lesson_by_code(self, code) -> Optional[SurfLesson]:
        return await SurfLesson.filter(unique_code=code).prefetch_related("surf_destination", "surf_type").first()

    async def get_booked_lesson_by_code(self, code) -> Optional[SurfLesson]:
        return await (
            SurfLesson.filter(unique_code=code)
            .prefetch_related("surf_destination", "surf_type", "user_surfs__user").first()
        )

    async def get_all_booked_lessons_future(self) -> list[SurfLesson]:
        all_lessons = await (
            SurfLesson.filter(user_surfs__isnull=False)
            .distinct()
            .prefetch_related("surf_destination", "user_surfs__user", "surf_type")
            .order_by("start_date")
        )

        today = date.today()
        result = []
        for l in all_lessons:
            if safe_parse_date(l.start_date) >= today:
                result.append(l)
        return result

    async def get_all_lessons_by_dest(self, destination_name) -> list[SurfLesson]:
        all_lessons = await (
            SurfLesson.filter(surf_destination__destination=destination_name)
            .prefetch_related("surf_destination", "surf_type")
            .order_by("start_date")
        )

        today = date.today()
        return [
            l for l in all_lessons
            if safe_parse_date(l.start_date) >= today
        ]

    async def get_upcoming_user_lessons(self, tg_id) -> list[UserSurf]:
        all_surfs = await (
            UserSurf.filter(user__user_tg_id=tg_id)
            .prefetch_related("surf__surf_destination", "surf__surf_type")
            .order_by("surf__start_date")
        )

        today = date.today()
        result = []
        for us in all_surfs:
            if safe_parse_date(us.surf.start_date) >= today:
                result.append(us)
        return result

    async def get_user_lesson_details(self, tg_id, code) -> UserSurf:
        return await UserSurf.filter(
            user__user_tg_id=tg_id,
            surf__unique_code=code
        ).prefetch_related("surf__surf_destination", "surf__surf_type").first()

    async def get_user_lesson_payment(self, user_id, surf_id) -> SurfPayment:
        return await SurfPayment.filter(
            user_id=user_id,
            surf_id=surf_id
        ).first()

    async def get_future_paid_lesson(self, code) -> SurfLesson | None:
        lesson = await self.get_lesson_by_code(code)
        if not lesson:
            return None
        if safe_parse_date(lesson.start_date) < date.today() or not await SurfPayment.filter(surf=lesson).exists():
            return None
        return lesson

    """LESSON UPDATE"""

    async def reduce_places_on_lesson(self, code, count) -> bool | None:
        lesson = await self.get_lesson_by_code(code)
        if not lesson:
            return None
        if lesson.surf_places < count:
            return False
        lesson.surf_places -= count
        await lesson.save()
        return True

    async def add_places_on_lesson(self, code, count) -> bool | None:
        lesson = await self.get_lesson_by_code(code)
        if not lesson:
            return None
        lesson.surf_places += count
        await lesson.save()
        return True

    """LESSON DELETE"""

    async def delete_lesson(self, code) -> bool:
        deleted = await SurfLesson.filter(unique_code=code).delete()
        return deleted > 0
