import pytest
from unittest.mock import Mock
from sqlalchemy.exc import SQLAlchemyError,OperationalError

from app.taskapp.exceptions import CollectionOperationException, CollectionNotFoundException
from app.taskapp.model import DocumentCreate, DocumentUpdate


@pytest.mark.unit
@pytest.mark.taskapp
class TestCollectionServiceCreate:
    def test_create_collection_success(self, mock_document_service, valid_collection_create):
        mock_document_service.db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 1))
        collection_id = mock_document_service.create_document(
            user_id=1,
            doc_col_data=valid_collection_create
        )
        assert collection_id == 1
        mock_document_service.db.add.assert_called_once()
        mock_document_service.db.commit.assert_called_once()

    def test_create_collection_db_err(self, mock_document_service, valid_collection_create):
        mock_document_service.db.commit.side_effect = OperationalError('DB Error', None, None)

        with pytest.raises(CollectionOperationException):
            mock_document_service.create_document(
                user_id=1,
                doc_col_data=valid_collection_create
            )
        mock_document_service.db.rollback.assert_called_once()

    def test_create_collection_all_fields(self, mock_document_service, valid_collection_data):
        mock_document_service.db.refresh = Mock(side_effect=lambda obj: setattr(obj, 'id', 5))
        collection_id = mock_document_service.create_document(
            user_id=1,
            doc_col_data=DocumentCreate(**valid_collection_data)
        )

        assert collection_id == 5
        mock_document_service.db.add.assert_called_once()

    def test_create_collection_only_title(self, mock_document_service, valid_collection_data):
        valid_collection_data.pop('description')
        mock_document_service.db.refresh = Mock(
            side_effect=lambda obj: setattr(obj, 'id', 3)
        )
        collection_id = mock_document_service.create_document(
            user_id=1,
            doc_col_data=DocumentCreate(**valid_collection_data)
        )

        assert collection_id == 3
        mock_document_service.db.add.assert_called_once()

@pytest.mark.unit
@pytest.mark.taskapp
class TestCollectionServiceFetch:
    def test_fetch_all_collections_success(self, mock_document_service, multiple_collection_entity):
        mock_document_service.db.query.return_value.filter_by.return_value.all.return_value = multiple_collection_entity

        collections = mock_document_service.fetch_documents(user_id=1)

        mock_document_service.db.query.return_value.filter_by.assert_called_once_with(user_id=1)
        assert len(collections) == 4
        assert all(hasattr(col, 'id') for col in collections)

    def test_fetch_all_collections_empty(self, mock_document_service):
        mock_document_service.db.query.return_value.filter_by.return_value.all.return_value = []

        collections = mock_document_service.fetch_documents(user_id=1)

        assert collections == []

    def test_fetch_all_collections_db_err(self, mock_document_service):
        mock_document_service.db.query.return_value.filter_by.return_value.all.side_effect = OperationalError('DB Error', None, None)

        with pytest.raises(CollectionOperationException):
            mock_document_service.fetch_documents(user_id=1)

    def test_fetch_collection_by_id_success(self, mock_document_service, sample_collection_entity):
        mock_document_service.db.query.return_value.filter_by.return_value.first.return_value = sample_collection_entity

        collection = mock_document_service.fetch_document_by_id(
            user_id=1,
            document_id=1
        )

        assert collection.id == 1
        assert collection.title == sample_collection_entity.title

    def test_fetch_collection_by_id_not_found(self, mock_document_service):
        mock_document_service.db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(CollectionNotFoundException):
            mock_document_service.fetch_document_by_id(
                user_id=1,
                document_id=999
            )

    def test_fetch_collection_by_id_db_err(self, mock_document_service):
        mock_document_service.db.query.return_value.filter_by.return_value.first.side_effect = SQLAlchemyError('DB Error')

        with pytest.raises(CollectionOperationException):
            mock_document_service.fetch_document_by_id(
                user_id=1,
                document_id=1
            )

@pytest.mark.unit
@pytest.mark.taskapp
class TestCollectionServiceUpdate:
    def test_update_collection_success(self, mock_document_service, sample_collection_entity, valid_collection_update):
        mock_document_service.db.query.return_value.filter_by.return_value.first.return_value = sample_collection_entity

        mock_document_service.update_document(
            user_id=1,
            document_id=1,
            doc_col_data=valid_collection_update
        )
        mock_document_service.db.commit.assert_called_once()
        mock_document_service.db.refresh.assert_called_once()

    def test_update_collection_not_found(self, mock_document_service, valid_collection_update):
        mock_document_service.db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(CollectionNotFoundException):
            mock_document_service.update_document(
                user_id=1,
                document_id=99,
                doc_col_data=valid_collection_update
            )

    def test_update_collection_title(self, mock_document_service, sample_collection_entity, valid_collection_data):
        mock_document_service.db.query.return_value.filter_by.return_value.first.return_value = sample_collection_entity
        valid_collection_data.pop('description')

        mock_document_service.update_document(
            user_id=1,
            document_id=1,
            doc_col_data=DocumentUpdate(**valid_collection_data)
        )
        mock_document_service.db.commit.assert_called_once()

    def test_update_partial_desc(self, mock_document_service, sample_collection_entity, valid_collection_data):
        mock_document_service.db.query.return_value.filter_by.return_value.first.return_value = sample_collection_entity
        valid_collection_data.pop('title')

        mock_document_service.update_document(
            user_id=1,
            document_id=1,
            doc_col_data=DocumentUpdate(**valid_collection_data)
        )
        mock_document_service.db.commit.assert_called_once()

    def test_update_collection_db_err(self, mock_document_service, sample_collection_entity, valid_collection_update):
        mock_document_service.db.query.return_value.filter_by.return_value.first.return_value = sample_collection_entity
        mock_document_service.db.commit.side_effect = OperationalError('DB Error', None, None)

        with pytest.raises(CollectionOperationException):
            mock_document_service.update_document(
                user_id=1,
                document_id=1,
                doc_col_data=valid_collection_update
            )

        mock_document_service.db.rollback.assert_called_once()

@pytest.mark.unit
@pytest.mark.taskapp
class TestCollectionServiceDelete:
    def test_delete_collection_success(self, mock_document_service, sample_collection_entity):
        mock_document_service.db.query.return_value.filter_by.return_value.first.return_value = sample_collection_entity
        mock_document_service.delete_collection(
            user_id=1,
            collection_id=1
        )
        mock_document_service.db.delete.assert_called_once_with(sample_collection_entity)
        mock_document_service.db.commit.assert_called_once()

    def test_delete_collection_not_found(self, mock_document_service):
        mock_document_service.db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(CollectionNotFoundException):
            mock_document_service.delete_collection(
                user_id=1,
                collection_id=99
            )

    def test_delete_collection_db_err(self, mock_document_service, sample_collection_entity):
        mock_document_service.db.query.return_value.filter_by.return_value.first.return_value = sample_collection_entity
        mock_document_service.db.commit.side_effect = OperationalError('DB Error', None, None)

        with pytest.raises(CollectionOperationException):
            mock_document_service.delete_collection(
                user_id=1,
                collection_id=1
            )
        mock_document_service.db.rollback.assert_called_once()

    def test_delete_verifies_user_ownership(self, mock_document_service):
        mock_query = Mock()
        mock_document_service.db.query.return_value = mock_query
        mock_query.filter_by.return_value.first.return_value = None

        with pytest.raises(CollectionNotFoundException):
            mock_document_service.delete_collection(
                user_id=2,
                collection_id=1
            )
        mock_query.filter_by.assert_called_once()