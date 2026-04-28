import os

from app.fileapp.model import FileRead
from app.fileapp.services.base_service import FileService
from app.logger import get_logger
from app.fileapp.exceptions import FileNotFoundException

logger = get_logger(__name__)


class FileDownloadService(FileService):
    def get_file_path(self, user_id: int, file_id: int) -> FileRead:
        file = self._get_file_instance(user_id, file_id)

        if not os.path.exists(file.file_path):
            logger.error("Physical file missing", file_id=file_id, path=file.file_path)
            raise FileNotFoundException(f"file-{file_id} not found")

        return FileRead.model_validate(file)
