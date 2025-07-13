import logging
import utils.export

logger = logging.getLogger(__name__)


class ExportService:

    @staticmethod
    async def export_db():
        try:
            export = await utils.export.export_all_models_to_excel()
            if export is None or export.getbuffer().nbytes == 0:
                return False
            return export
        except Exception as e:
            logger.error(e)
            return False
