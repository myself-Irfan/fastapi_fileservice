import io
from datetime import datetime
import pytest
from unittest.mock import Mock, mock_open, patch
from sqlalchemy.exc import SQLAlchemyError

from app.fileapp.exceptions import (
    DocumentNotFoundException,
    FileUploadException,
    InvalidFileTypeException,
)
from app.fileapp.services.upload_service import FileUploadService


@pytest.fixture
def upload_service(mock_db_session, tmp_path, mocker):
    mocker.patch("app.fileapp.services.upload_service.settings.upload_dir", tmp_path)
    return FileUploadService(db=mock_db_session)


def _make_upload_file(filename="test.txt", content=b"hello test content"):
    f = Mock()
    f.filename = filename
    f.file = io.BytesIO(content)
    return f


def _refresh_side_effect(obj):
    """mimics what a real db.refresh() would populate after insert, for FileRead validation"""
    obj.id = 1
    obj.is_active = True
    obj.created_at = datetime.now()


@pytest.mark.unit
@pytest.mark.fileapp
class TestFileUploadServiceUpload:
    def test_upload_new_file_creates_db_record(self, upload_service, mocker):
        mock_file = _make_upload_file("test.txt", b"hello content")
        mocker.patch(
            "app.fileapp.services.upload_service.magic.from_file",
            return_value="text/plain",
        )
        upload_service.db.query.return_value.filter_by.return_value.first.return_value = None
        upload_service.db.refresh = Mock(side_effect=_refresh_side_effect)

        upload_service.upload_file(file=mock_file, user_id=1, document_id=None)

        upload_service.db.add.assert_called_once()
        upload_service.db.commit.assert_called_once()

    def test_upload_dedup_reuses_existing_file_path(self, upload_service, mocker):
        mock_file = _make_upload_file("test.txt", b"hello content")
        existing = Mock()
        existing.id = 42
        existing.file_path = "/uploads/existing_deadbeef.txt"

        mocker.patch(
            "app.fileapp.services.upload_service.magic.from_file",
            return_value="text/plain",
        )
        upload_service.db.query.return_value.filter_by.return_value.first.return_value = existing
        upload_service.db.refresh = Mock(side_effect=_refresh_side_effect)

        upload_service.upload_file(file=mock_file, user_id=1, document_id=None)

        added_entity = upload_service.db.add.call_args[0][0]
        assert added_entity.file_path == existing.file_path

    def test_upload_raises_document_not_found(self, upload_service):
        upload_service.db.get.return_value = None

        with pytest.raises(DocumentNotFoundException):
            upload_service.upload_file(
                file=_make_upload_file(), user_id=1, document_id=999
            )

    def test_upload_raises_invalid_type_bad_extension(self, upload_service, mocker):
        mock_file = _make_upload_file("malware.exe", b"MZ\x90\x00")
        mocker.patch(
            "app.fileapp.services.upload_service.magic.from_file",
            return_value="application/x-dosexec",
        )

        with pytest.raises(InvalidFileTypeException):
            upload_service.upload_file(file=mock_file, user_id=1, document_id=None)

    def test_upload_raises_invalid_type_on_mime_mismatch(self, upload_service, mocker):
        mock_file = _make_upload_file("fake.txt", b"MZ\x90\x00")
        mocker.patch(
            "app.fileapp.services.upload_service.magic.from_file",
            return_value="application/x-dosexec",
        )

        with pytest.raises(InvalidFileTypeException):
            upload_service.upload_file(file=mock_file, user_id=1, document_id=None)

    def test_upload_db_error_rolls_back(self, upload_service, mocker):
        mock_file = _make_upload_file("test.txt", b"hello content")
        mocker.patch(
            "app.fileapp.services.upload_service.magic.from_file",
            return_value="text/plain",
        )
        upload_service.db.query.return_value.filter_by.return_value.first.return_value = None
        upload_service.db.commit.side_effect = SQLAlchemyError("DB Error")

        with pytest.raises(FileUploadException):
            upload_service.upload_file(file=mock_file, user_id=1, document_id=None)

        upload_service.db.rollback.assert_called_once()

    def test_upload_cleans_temp_file_on_invalid_type(self, upload_service, mocker):
        mock_file = _make_upload_file("fake.txt", b"content")
        mocker.patch(
            "app.fileapp.services.upload_service.magic.from_file",
            return_value="application/x-dosexec",
        )
        mock_remove = mocker.patch("app.fileapp.services.upload_service.os.remove")

        with pytest.raises(InvalidFileTypeException):
            upload_service.upload_file(file=mock_file, user_id=1, document_id=None)

        mock_remove.assert_called_once()

    def test_upload_with_valid_document_id_succeeds(self, upload_service, mocker):
        mock_file = _make_upload_file("test.txt", b"hello content")
        mocker.patch(
            "app.fileapp.services.upload_service.magic.from_file",
            return_value="text/plain",
        )
        upload_service.db.get.return_value = Mock()
        upload_service.db.query.return_value.filter_by.return_value.first.return_value = None
        upload_service.db.refresh = Mock(side_effect=_refresh_side_effect)

        upload_service.upload_file(file=mock_file, user_id=1, document_id=5)

        added_entity = upload_service.db.add.call_args[0][0]
        assert added_entity.document_id == 5

    def test_upload_sets_correct_user_id(self, upload_service, mocker):
        mock_file = _make_upload_file("test.txt", b"hello content")
        mocker.patch(
            "app.fileapp.services.upload_service.magic.from_file",
            return_value="text/plain",
        )
        upload_service.db.query.return_value.filter_by.return_value.first.return_value = None
        upload_service.db.refresh = Mock(side_effect=_refresh_side_effect)

        upload_service.upload_file(file=mock_file, user_id=42, document_id=None)

        added_entity = upload_service.db.add.call_args[0][0]
        assert added_entity.user_id == 42
