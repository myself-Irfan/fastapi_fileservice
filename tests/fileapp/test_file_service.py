import pytest
from unittest.mock import Mock, patch
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from app.fileapp.exceptions import FileNotFoundException, FileOperationException



@pytest.mark.unit
@pytest.mark.fileapp
class TestFileServiceFetch:
    def test_fetch_files_success(self, mock_file_service, multiple_file_entities):
        mock_file_service.db.query.return_value.filter_by.return_value.all.return_value = multiple_file_entities

        files = mock_file_service.fetch_files(user_id=1)

        assert len(files) == 3

    def test_fetch_files_with_document_id_filter(self, mock_file_service, multiple_file_entities):
        mock_file_service.db.query.return_value.filter_by.return_value.filter_by.return_value.all.return_value = [
            multiple_file_entities[0]
        ]

        files = mock_file_service.fetch_files(user_id=1, document_id=5)

        assert len(files) == 1

    def test_fetch_files_empty(self, mock_file_service):
        mock_file_service.db.query.return_value.filter_by.return_value.all.return_value = []

        files = mock_file_service.fetch_files(user_id=1)

        assert files == []

    def test_fetch_files_db_error(self, mock_file_service):
        mock_file_service.db.query.return_value.filter_by.return_value.all.side_effect = SQLAlchemyError(
            "DB Error"
        )

        with pytest.raises(FileOperationException):
            mock_file_service.fetch_files(user_id=1)

    def test_fetch_file_by_id_success(self, mock_file_service, sample_file_entity):
        mock_file_service.db.query.return_value.filter_by.return_value.first.return_value = (
            sample_file_entity
        )

        file = mock_file_service.fetch_file_by_id(user_id=1, file_id=1)

        assert file.id == 1
        assert file.title == sample_file_entity.title
        assert file.mime_type == sample_file_entity.mime_type

    def test_fetch_file_by_id_not_found(self, mock_file_service):
        mock_file_service.db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(FileNotFoundException):
            mock_file_service.fetch_file_by_id(user_id=1, file_id=999)

    def test_fetch_file_by_id_db_error(self, mock_file_service):
        mock_file_service.db.query.return_value.filter_by.return_value.first.side_effect = (
            OperationalError("DB Error", None, None)
        )

        with pytest.raises(FileOperationException):
            mock_file_service.fetch_file_by_id(user_id=1, file_id=1)

    def test_fetch_file_verifies_user_ownership(self, mock_file_service):
        mock_file_service.db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(FileNotFoundException):
            mock_file_service.fetch_file_by_id(user_id=99, file_id=1)

        mock_file_service.db.query.return_value.filter_by.assert_called_with(
            id=1, user_id=99, is_active=True
        )


@pytest.mark.unit
@pytest.mark.fileapp
class TestFileServiceDelete:
    def test_delete_file_soft_deletes_record(self, mock_file_service, sample_file_entity):
        get_query = Mock()
        get_query.filter_by.return_value.first.return_value = sample_file_entity
        count_query = Mock()
        count_query.filter.return_value.count.return_value = 1
        mock_file_service.db.query.side_effect = [get_query, count_query]

        with patch("app.fileapp.services.base_service.os.path.exists"), patch(
            "app.fileapp.services.base_service.os.remove"
        ) as mock_remove:
            result = mock_file_service.delete_file(user_id=1, file_id=1)

        assert result is True
        assert sample_file_entity.is_active is False
        mock_file_service.db.commit.assert_called_once()
        mock_remove.assert_not_called()

    def test_delete_file_hard_deletes_physical_when_last_ref(
        self, mock_file_service, sample_file_entity
    ):
        get_query = Mock()
        get_query.filter_by.return_value.first.return_value = sample_file_entity
        count_query = Mock()
        count_query.filter.return_value.count.return_value = 0
        mock_file_service.db.query.side_effect = [get_query, count_query]

        with patch(
            "app.fileapp.services.base_service.os.path.exists", return_value=True
        ), patch("app.fileapp.services.base_service.os.remove") as mock_remove:
            mock_file_service.delete_file(user_id=1, file_id=1)

        mock_remove.assert_called_once_with(sample_file_entity.file_path)

    def test_delete_file_preserves_physical_when_other_refs_exist(
        self, mock_file_service, sample_file_entity
    ):
        get_query = Mock()
        get_query.filter_by.return_value.first.return_value = sample_file_entity
        count_query = Mock()
        count_query.filter.return_value.count.return_value = 2
        mock_file_service.db.query.side_effect = [get_query, count_query]

        with patch("app.fileapp.services.base_service.os.path.exists"), patch(
            "app.fileapp.services.base_service.os.remove"
        ) as mock_remove:
            mock_file_service.delete_file(user_id=1, file_id=1)

        mock_remove.assert_not_called()

    def test_delete_file_skips_remove_if_physical_missing(
        self, mock_file_service, sample_file_entity
    ):
        get_query = Mock()
        get_query.filter_by.return_value.first.return_value = sample_file_entity
        count_query = Mock()
        count_query.filter.return_value.count.return_value = 0
        mock_file_service.db.query.side_effect = [get_query, count_query]

        with patch(
            "app.fileapp.services.base_service.os.path.exists", return_value=False
        ), patch("app.fileapp.services.base_service.os.remove") as mock_remove:
            mock_file_service.delete_file(user_id=1, file_id=1)

        mock_remove.assert_not_called()

    def test_delete_file_not_found(self, mock_file_service):
        mock_file_service.db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(FileNotFoundException):
            mock_file_service.delete_file(user_id=1, file_id=999)

    def test_delete_file_db_error_rolls_back(self, mock_file_service, sample_file_entity):
        get_query = Mock()
        get_query.filter_by.return_value.first.return_value = sample_file_entity
        mock_file_service.db.query.side_effect = [get_query]
        mock_file_service.db.commit.side_effect = SQLAlchemyError("DB Error")

        with pytest.raises(FileOperationException):
            mock_file_service.delete_file(user_id=1, file_id=1)

        mock_file_service.db.rollback.assert_called_once()

    def test_delete_verifies_user_ownership(self, mock_file_service):
        mock_file_service.db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(FileNotFoundException):
            mock_file_service.delete_file(user_id=99, file_id=1)

        mock_file_service.db.query.return_value.filter_by.assert_called_with(
            id=1, user_id=99, is_active=True
        )
