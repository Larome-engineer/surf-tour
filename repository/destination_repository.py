import logging
from database.models import Destination

logger = logging.getLogger(__name__)


class DestRepository:
    async def create_destination(self, destination: Destination) -> Destination:
        try:
            return await Destination.create(destination=destination.destination)
        except Exception as e:
            logger.error(f"Failed to create_destination: {destination}, {str(e)}")
            raise

    async def get_destination_by_name(self, name: str) -> Destination:
        try:
            return await Destination.get_or_none(destination=name.lower())
        except Exception as e:
            logger.error(f"Failed to get_dest_by_name: {name}, {str(e)}")
            raise

    async def get_all_destinations(self) -> list[Destination]:
        try:
            return await Destination.all()
        except Exception as e:
            logger.error(f"Failed to get_all_destinations: {str(e)}")
            raise

    async def delete_destination_by_name(self, name) -> bool:
        try:
            deleted = await Destination.filter(destination=name).delete()
            return deleted > 0
        except Exception as e:
            logger.error(f"Failed to delete_destination_by_name: {name}, {str(e)}")
            raise
