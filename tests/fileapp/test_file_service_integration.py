import uuid
import pytest

from app.fileapp.entities import DocumentCollectionFile
from app.fileapp.exceptions import FileNotFoundException


def _make_file_record(user_id: int, document_id=None):
    return DocumentCollectionFile(
        title="integration_file.txt",
        is_active=True,
        file_path="/tmp/nonexistent.txt",
        file_size=512,
        mime_type="text/plain",
        extension=".txt",
        checksum=(uuid.uuid4().hex * 2)[:64],
        user_id=user_id,
        document_id=document_id,
    )


@pytest.mark.unit
@pytest.mark.fileapp
class TestFileServiceIntegration:
    def test_fetch_files_returns_active_records(self, file_service, db_session, make_test_user):
        record = _make_file_record(make_test_user.id)
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)

        files = file_service.fetch_files(user_id=make_test_user.id)

        assert any(f.id == record.id for f in files)

    def test_fetch_files_excludes_inactive(self, file_service, db_session, make_test_user):
        record = _make_file_record(make_test_user.id)
        record.is_active = False
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)

        files = file_service.fetch_files(user_id=make_test_user.id)

        assert not any(f.id == record.id for f in files)

    def test_fetch_files_with_document_id_filter(self, file_service, db_session, make_test_user):
        with_doc = _make_file_record(make_test_user.id, document_id=None)
        db_session.add(with_doc)
        db_session.commit()

        files = file_service.fetch_files(user_id=make_test_user.id, document_id=99999)

        assert all(f.document_id == 99999 for f in files)

    def test_fetch_file_by_id_success(self, file_service, db_session, make_test_user):
        record = _make_file_record(make_test_user.id)
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)

        result = file_service.fetch_file_by_id(user_id=make_test_user.id, file_id=record.id)

        assert result.id == record.id
        assert result.title == record.title
        assert result.mime_type == record.mime_type

    def test_fetch_file_by_id_not_found(self, file_service, make_test_user):
        with pytest.raises(FileNotFoundException):
            file_service.fetch_file_by_id(user_id=make_test_user.id, file_id=999999)

    def test_fetch_file_user_isolation(self, file_service, db_session, make_test_user):
        other_user_id = make_test_user.id + 9999
        record = _make_file_record(other_user_id)
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)

        with pytest.raises(FileNotFoundException):
            file_service.fetch_file_by_id(user_id=make_test_user.id, file_id=record.id)

    def test_delete_file_sets_inactive(self, file_service, db_session, make_test_user):
        record = _make_file_record(make_test_user.id)
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        file_id = record.id

        file_service.delete_file(user_id=make_test_user.id, file_id=file_id)

        db_session.expire_all()
        updated = db_session.get(DocumentCollectionFile, file_id)
        assert updated.is_active is False

    def test_delete_file_not_found(self, file_service, make_test_user):
        with pytest.raises(FileNotFoundException):
            file_service.delete_file(user_id=make_test_user.id, file_id=999999)

    def test_delete_then_fetch_raises_not_found(self, file_service, db_session, make_test_user):
        record = _make_file_record(make_test_user.id)
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)

        file_service.delete_file(user_id=make_test_user.id, file_id=record.id)

        with pytest.raises(FileNotFoundException):
            file_service.fetch_file_by_id(user_id=make_test_user.id, file_id=record.id)

    def test_fetch_files_user_isolation(self, file_service, db_session, make_test_user):
        other_user_id = make_test_user.id + 8888
        record = _make_file_record(other_user_id)
        db_session.add(record)
        db_session.commit()

        files = file_service.fetch_files(user_id=make_test_user.id)

        assert not any(f.id == record.id for f in files)
