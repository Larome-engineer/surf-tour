import logging

from database.models import Destination
from repository.destination_repository import DestRepository
from utils.serializer import serialize_destination

logger = logging.getLogger(__name__)


class DestService:
    def __init__(self, dest_repo: DestRepository):
        self.repo = dest_repo

    async def create_destination(self, name: str):
        dest = await self.repo.get_destination_by_name(name.lower())
        if dest is None:
            await self.repo.create_destination(
                Destination(destination=name.lower())
            )
            return True
        else:
            return False

    async def get_destination(self, name: str):
        d = await self.repo.get_destination_by_name(name.lower())
        if not d:
            return None
        return d

    async def get_all_destinations(self):
        dest = await self.repo.get_all_destinations()
        if not dest:
            return None
        return [serialize_destination(dest=d) for d in dest]

    async def delete_destination_by_name(self, name: str):
        await self.repo.delete_destination_by_name(name.lower())
        return True
