from fastapi import status
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session
from typing import List, Optional

from app.logger import get_logger
from app.taskapp.entities import DocumentCollection
from app.taskapp.model import DocumentRead, DocumentCreate, DocumentUpdate
from app.taskapp.exceptions import CollectionNotFoundException, CollectionOperationException

logger = get_logger(__name__)


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def _get_document_instance(self, user_id: int, collection_id: Optional[int]) -> DocumentCollection:
        try:
            collection: DocumentCollection | None = self.db.query(DocumentCollection).filter_by(
                id=collection_id,
                user_id=user_id
            ).first()
        except (SQLAlchemyError, OperationalError) as db_err:
            logger.error('document collection retrival failed', collection_id=collection_id, error=db_err, exc_info=True)
            raise CollectionOperationException(
                message=f'database error while retrieving collection-{collection_id}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from db_err
        else:
            if not collection:
                logger.warning('collection not found', collection_id=collection_id)
                raise CollectionNotFoundException(f'collection-{collection_id} not found')
            return collection

    def fetch_documents(self, user_id: int) -> List[DocumentRead]:
        try:
            documents = self.db.query(DocumentCollection).filter_by(
                user_id=user_id
            ).all()

            return [DocumentRead.model_validate(document) for document in documents]
        except (SQLAlchemyError, OperationalError) as db_err:
            logger.error("document collections retrieval failed", error=db_err, exc_info=True)
            raise CollectionOperationException(
                message="database error while retrieving document collections",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from db_err

    def fetch_document_by_id(self, user_id: int, document_id: int) -> DocumentRead:
        document: DocumentCollection = self._get_document_instance(user_id, document_id)
        return DocumentRead.model_validate(document)

    def create_document(self, user_id: int, doc_col_data: DocumentCreate) -> int:
        try:
            new_doc_col: DocumentCollection = DocumentCollection(**doc_col_data.model_dump(), user_id=user_id)
            self.db.add(new_doc_col)
            self.db.commit()
            self.db.refresh(new_doc_col)

            return new_doc_col.id
        except (SQLAlchemyError, OperationalError) as db_err:
            self.db.rollback()
            logger.error("document collection creation failed", error=db_err, exc_info=True)
            raise CollectionOperationException(
                message=f"Database error while creating task",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from db_err

    def update_document(self, user_id: int, document_id: int, doc_col_data: DocumentUpdate) -> None:
        try:
            document: DocumentCollection = self._get_document_instance(user_id, document_id)

            for key, value in doc_col_data.model_dump(exclude_unset=True).items():
                setattr(document, key, value)

            self.db.commit()
            self.db.refresh(document)

            logger.info("document collection update successful", collection_id=document.id)
        except CollectionNotFoundException:
            logger.warning("collection update failed - not found", collection_id=document_id)
            raise CollectionNotFoundException(f'update failed: collection-{document_id} not found')
        except (SQLAlchemyError, OperationalError) as db_err:
            self.db.rollback()
            logger.error("document update failed", error=db_err, document_id=document_id, exc_info=True)
            raise CollectionOperationException(
                message=f"database error while updating collection-{document_id}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from db_err

    def delete_collection(self, user_id: int, collection_id: int) -> None:
        try:
            collection = self._get_document_instance(user_id, collection_id)
            self.db.delete(collection)
            self.db.commit()
            logger.info("document collection deletion successful", collection_id=collection_id)
        except CollectionNotFoundException:
            logger.warning("collection deletion failed", error="collection not found", collection_id=collection_id)
            raise CollectionNotFoundException(f'deletion failed: collection-{collection_id} not found')
        except (SQLAlchemyError, OperationalError) as db_err:
            self.db.rollback()
            logger.error("collection deletion failed", collection_id=collection_id, error=db_err, exc_info=True)
            raise CollectionOperationException(
                message=f'database error while deleting collection-{collection_id}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from db_err