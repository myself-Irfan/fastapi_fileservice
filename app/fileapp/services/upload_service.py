import dataclasses
import mimetypes
import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional, Set, cast

import magic
from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.utils import calculate_checksum
from app.logger import get_logger
from app.fileapp.entities import DocumentCollectionFile
from app.fileapp.exceptions import DocumentNotFoundException, InvalidFileTypeException, FileProcessingException, FileUploadException
from app.fileapp.value_objects import FileMetadata
from app.collectionapp.entities import DocumentCollection

logger = get_logger(__name__)


class FileUploadService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = settings.upload_dir
        self.upload_dir.mkdir(exist_ok=True)

        self.allowed_extensions: Set[str] = settings.allowed_extensions_set

        self.extension_to_mime = {}
        for ext in self.allowed_extensions:
            mime_type, _ = mimetypes.guess_type(f"file{ext}")
            if mime_type:
                self.extension_to_mime[ext] = mime_type

        self.allowed_mime_types = set(self.extension_to_mime.values())

    def __check_document_collection_exist(self, document_id: int) -> bool:
        return self.db.get(DocumentCollection, document_id) is not None

    def __save_temp_file(self, file: UploadFile) -> Path:
        temp_filename = f"temp_{os.urandom(8).hex()}_{file.filename}"
        temp_path = self.upload_dir / temp_filename

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(cast(BinaryIO, file.file), buffer)

        return temp_path

    def __validate_file_type(self, temp_path: Path, file_name: str) -> Optional[str]:
        extension = Path(file_name).suffix.lower()
        real_mime_type = magic.from_file(str(temp_path), mime=True)

        if extension not in self.allowed_extensions:
            logger.warning("file type not allowed", filename=file_name)
            return None

        expected_mime = self.extension_to_mime.get(extension)
        if real_mime_type != expected_mime:
            logger.warning(
                "file rejected — type does not match extension",
                filename=file_name,
                expected_type=expected_mime,
                detected_type=real_mime_type,
            )
            return None

        return real_mime_type

    def __resolve_file_path(self, checksum: str, extension: str, temp_path: Path) -> str:
        existing = (
            self.db.query(DocumentCollectionFile)
            .filter_by(checksum=checksum)
            .first()
        )
        if existing:
            logger.info("file deduplicated", checksum=checksum[:8], existing_file_id=existing.id)
            os.remove(temp_path)
            return str(existing.file_path)

        final_path = str(self.upload_dir / f"{checksum}{extension}")
        shutil.move(str(temp_path), final_path)
        logger.info("new file saved", path=final_path)
        return final_path

    def __build_metadata(self, file: UploadFile, temp_path: Path, detected_mime: str) -> FileMetadata:
        extension = Path(file.filename).suffix.lower()
        checksum = calculate_checksum(str(temp_path))
        file_size = os.path.getsize(temp_path)  # measure before temp is moved or deleted
        file_path = self.__resolve_file_path(checksum, extension, temp_path)

        return FileMetadata(
            title=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=detected_mime,
            extension=extension,
            checksum=checksum,
        )

    def upload_file(self, file: UploadFile, user_id: int, document_id: Optional[int] = None):
        temp_path = None

        if document_id is not None and not self.__check_document_collection_exist(document_id):
            raise DocumentNotFoundException(f"document_collection-{document_id} does not exist")

        try:
            temp_path = self.__save_temp_file(file)

            detected_mime = self.__validate_file_type(temp_path, file.filename)
            if detected_mime is None:
                raise InvalidFileTypeException("file type mismatch or not allowed")

            metadata = self.__build_metadata(file, temp_path, detected_mime)
            temp_path = None  # temp consumed inside __build_metadata

            new_file = DocumentCollectionFile(
                **dataclasses.asdict(metadata),
                user_id=user_id,
                document_id=document_id,
            )
            self.db.add(new_file)
            self.db.commit()
            self.db.refresh(new_file)

            logger.info("file record creation successful", file_id=new_file.id)

        except SQLAlchemyError as sql_err:
            self.db.rollback()
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error("file upload failed", error_type="database error", error=sql_err, exc_info=True)
            raise FileProcessingException("database error during file upload") from sql_err
        except FileUploadException:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error("file upload failed", error_type="unexpected error", error=e, exc_info=True)
            raise FileProcessingException(f"unexpected error during file upload: {str(e)}") from e