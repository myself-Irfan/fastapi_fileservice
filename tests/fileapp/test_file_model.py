import pytest
from datetime import datetime
from pydantic import ValidationError

from app.fileapp.model import FileBase, FileCreate, FileUpdate, FileRead, FileReadResponse, FileListResponse


@pytest.mark.unit
@pytest.mark.fileapp
class TestFileBaseModel:
    def test_valid_title(self):
        f = FileBase(title="My Document")
        assert f.title == "My Document"

    def test_title_required(self):
        with pytest.raises(ValidationError) as exc:
            FileBase()
        assert any(e["loc"] == ("title",) for e in exc.value.errors())

    def test_title_empty_string(self):
        with pytest.raises(ValidationError) as exc:
            FileBase(title="")
        assert any(e["loc"] == ("title",) for e in exc.value.errors())

    def test_title_max_length(self):
        with pytest.raises(ValidationError) as exc:
            FileBase(title="a" * 101)
        assert any(e["loc"] == ("title",) for e in exc.value.errors())

    def test_title_at_max_length(self):
        f = FileBase(title="a" * 100)
        assert len(f.title) == 100

    def test_title_min_length(self):
        f = FileBase(title="x")
        assert f.title == "x"

    def test_title_special_chars(self):
        f = FileBase(title="Report: Q1 & Q2 (2025)")
        assert f.title == "Report: Q1 & Q2 (2025)"


@pytest.mark.unit
@pytest.mark.fileapp
class TestFileCreateModel:
    def test_valid_file_create(self):
        f = FileCreate(title="report.pdf", document_id=1)
        assert f.title == "report.pdf"
        assert f.document_id == 1

    def test_document_id_required(self):
        with pytest.raises(ValidationError) as exc:
            FileCreate(title="report.pdf")
        assert any(e["loc"] == ("document_id",) for e in exc.value.errors())

    def test_title_required(self):
        with pytest.raises(ValidationError) as exc:
            FileCreate(document_id=1)
        assert any(e["loc"] == ("title",) for e in exc.value.errors())


@pytest.mark.unit
@pytest.mark.fileapp
class TestFileUpdateModel:
    def test_update_title_only(self):
        f = FileUpdate(title="new title")
        assert f.title == "new title"
        assert f.document_id is None

    def test_update_document_id_only(self):
        f = FileUpdate(document_id=5)
        assert f.document_id == 5
        assert f.title is None

    def test_update_both_fields(self):
        f = FileUpdate(title="new title", document_id=3)
        assert f.title == "new title"
        assert f.document_id == 3

    def test_update_empty_is_valid(self):
        f = FileUpdate()
        assert f.title is None
        assert f.document_id is None

    def test_extra_fields_forbidden(self):
        with pytest.raises(ValidationError):
            FileUpdate(title="ok", unknown_field="value")

    def test_title_min_length_enforced(self):
        with pytest.raises(ValidationError) as exc:
            FileUpdate(title="")
        assert any(e["loc"] == ("title",) for e in exc.value.errors())

    def test_title_max_length_enforced(self):
        with pytest.raises(ValidationError) as exc:
            FileUpdate(title="a" * 101)
        assert any(e["loc"] == ("title",) for e in exc.value.errors())

    def test_document_id_none_moves_to_standalone(self):
        f = FileUpdate(document_id=None)
        assert f.document_id is None


@pytest.mark.unit
@pytest.mark.fileapp
class TestFileReadModel:
    def _valid_data(self):
        return {
            "id": 1,
            "title": "report.pdf",
            "is_active": True,
            "file_size": 1024,
            "mime_type": "application/pdf",
            "extension": ".pdf",
            "checksum": "a" * 64,
            "created_at": datetime.now(),
            "updated_at": None,
            "document_id": None,
            "user_id": 1,
        }

    def test_valid_file_read(self):
        f = FileRead(**self._valid_data())
        assert f.id == 1
        assert f.title == "report.pdf"
        assert f.is_active is True

    def test_checksum_optional(self):
        data = self._valid_data()
        data["checksum"] = None
        f = FileRead(**data)
        assert f.checksum is None

    def test_updated_at_optional(self):
        data = self._valid_data()
        data["updated_at"] = None
        f = FileRead(**data)
        assert f.updated_at is None

    def test_document_id_optional(self):
        data = self._valid_data()
        data["document_id"] = None
        f = FileRead(**data)
        assert f.document_id is None

    def test_id_required(self):
        data = self._valid_data()
        data.pop("id")
        with pytest.raises(ValidationError) as exc:
            FileRead(**data)
        assert any(e["loc"] == ("id",) for e in exc.value.errors())

    def test_from_orm_attributes(self, sample_file_entity):
        f = FileRead.model_validate(sample_file_entity)
        assert f.id == sample_file_entity.id
        assert f.title == sample_file_entity.title
        assert f.mime_type == sample_file_entity.mime_type
        assert f.extension == sample_file_entity.extension


@pytest.mark.unit
@pytest.mark.fileapp
class TestFileResponseModels:
    def test_file_read_response_with_data(self, sample_file_entity):
        file_read = FileRead.model_validate(sample_file_entity)
        resp = FileReadResponse(message="ok", data=file_read)
        assert resp.message == "ok"
        assert resp.data.id == sample_file_entity.id

    def test_file_read_response_no_data(self):
        resp = FileReadResponse(message="file upload successful")
        assert resp.data is None

    def test_file_list_response(self, sample_file_entity):
        file_read = FileRead.model_validate(sample_file_entity)
        resp = FileListResponse(message="success", data=[file_read])
        assert len(resp.data) == 1
        assert resp.data[0].id == sample_file_entity.id

    def test_file_list_response_empty(self):
        resp = FileListResponse(message="no files", data=[])
        assert resp.data == []
