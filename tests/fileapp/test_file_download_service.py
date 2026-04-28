import pytest
from unittest.mock import Mock, patch

from app.fileapp.exceptions import FileNotFoundException, FileOperationException
from app.fileapp.services.download_service import FileDownloadService


@pytest.fixture
def mock_download_service(mock_db_session):
    return FileDownloadService(db=mock_db_session)


@pytest.mark.unit
@pytest.mark.fileapp
class TestFileDownloadService:
    def test_get_file_path_success(self, mock_download_service, sample_file_entity):
        mock_download_service.db.query.return_value.filter_by.return_value.first.return_value = (
            sample_file_entity
        )

        with patch(
            "app.fileapp.services.download_service.os.path.exists", return_value=True
        ):
            result = mock_download_service.get_file_path(user_id=1, file_id=1)

        assert result.id == sample_file_entity.id
        assert result.file_path == sample_file_entity.file_path

    def test_get_file_path_not_found_in_db(self, mock_download_service):
        mock_download_service.db.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        with pytest.raises(FileNotFoundException):
            mock_download_service.get_file_path(user_id=1, file_id=999)

    def test_get_file_path_physical_file_missing(
        self, mock_download_service, sample_file_entity
    ):
        mock_download_service.db.query.return_value.filter_by.return_value.first.return_value = (
            sample_file_entity
        )

        with patch(
            "app.fileapp.services.download_service.os.path.exists", return_value=False
        ):
            with pytest.raises(FileNotFoundException):
                mock_download_service.get_file_path(user_id=1, file_id=1)

    def test_get_file_path_returns_read_model(self, mock_download_service, sample_file_entity):
        mock_download_service.db.query.return_value.filter_by.return_value.first.return_value = (
            sample_file_entity
        )

        with patch(
            "app.fileapp.services.download_service.os.path.exists", return_value=True
        ):
            result = mock_download_service.get_file_path(user_id=1, file_id=1)

        assert result.mime_type == sample_file_entity.mime_type
        assert result.title == sample_file_entity.title
        assert result.extension == sample_file_entity.extension

    def test_get_file_path_verifies_user_ownership(self, mock_download_service):
        mock_download_service.db.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        with pytest.raises(FileNotFoundException):
            mock_download_service.get_file_path(user_id=99, file_id=1)

        mock_download_service.db.query.return_value.filter_by.assert_called_with(
            id=1, user_id=99, is_active=True
        )
