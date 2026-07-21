from fastapi import status
from functools import partial
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session
from typing import List, Optional

from app.logger import get_logger
from app.database.transaction import db_transaction
from app.collectionapp.entities import DocumentCollection
from app.collectionapp.models.read_document_model import DocumentReadModel
from app.collectionapp.models.create_document_model import DocumentCreateRequestModel
from app.collectionapp.models.update_document_model import DocumentUpdateRequestModel
from app.collectionapp.exceptions import CollectionNotFoundException, CollectionOperationException

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
            logger.error('document collection retrieval failed', collection_id=collection_id, error=db_err, exc_info=True)
            raise CollectionOperationException(
                message=f'database error while retrieving collection-{collection_id}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from db_err
        else:
            if not collection:
                logger.warning('collection not found', collection_id=collection_id)
                raise CollectionNotFoundException(f'collection-{collection_id} not found')
            return collection

    def fetch_documents(self, user_id: int) -> List[DocumentReadModel]:
        try:
            documents = self.db.query(DocumentCollection).filter_by(
                user_id=user_id
            ).all()

            return [DocumentReadModel.model_validate(document) for document in documents]
        except (SQLAlchemyError, OperationalError) as db_err:
            logger.error("document collections retrieval failed", error=db_err, exc_info=True)
            raise CollectionOperationException(
                message="database error while retrieving document collections",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from db_err

    def fetch_document_by_id(self, user_id: int, document_id: int) -> DocumentReadModel:
        document: DocumentCollection = self._get_document_instance(user_id, document_id)
        return DocumentReadModel.model_validate(document)

    def create_document(self, user_id: int, doc_col_data: DocumentCreateRequestModel) -> int:
        new_doc_col: DocumentCollection = DocumentCollection(**doc_col_data.model_dump(), user_id=user_id)
        on_error = partial(CollectionOperationException, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with db_transaction(self.db, on_error, "Database error while creating collection", refresh=[new_doc_col]):
            self.db.add(new_doc_col)

        return new_doc_col.id

    def update_document(self, user_id: int, document_id: int, doc_col_data: DocumentUpdateRequestModel) -> None:
        document: DocumentCollection = self._get_document_instance(user_id, document_id)
        on_error = partial(CollectionOperationException, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with db_transaction(self.db, on_error, f"database error while updating collection-{document_id}", refresh=[document], document_id=document_id):
            for key, value in doc_col_data.model_dump(exclude_unset=True).items():
                setattr(document, key, value)

        logger.info("document collection update successful", collection_id=document.id)

    def delete_collection(self, user_id: int, collection_id: int) -> None:
        collection = self._get_document_instance(user_id, collection_id)
        on_error = partial(CollectionOperationException, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with db_transaction(self.db, on_error, f'database error while deleting collection-{collection_id}', collection_id=collection_id):
            self.db.delete(collection)

        logger.info("document collection deletion successful", collection_id=collection_id)