import pytest
from pydantic import ValidationError
from datetime import datetime

from app.taskapp.model import DocumentCreate, DocumentUpdate, DocumentRead


@pytest.mark.unit
@pytest.mark.taskapp
class TestDocumentCreateModel:
    def test_valid_collection_create(self, valid_collection_data):
        document = DocumentCreate(**valid_collection_data)

        assert document.title == valid_collection_data['title']
        assert document.description == valid_collection_data['description']

    def test_short_title(self, valid_collection_data):
        valid_collection_data['title'] = ''

        with pytest.raises(ValidationError) as validation_err:
            DocumentCreate(**valid_collection_data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('title',) for error in errors)

    def test_long_title(self, valid_collection_data):
        valid_collection_data['title'] = valid_collection_data['title'] * 100

        with pytest.raises(ValidationError) as validation_err:
            DocumentCreate(**valid_collection_data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('title',) for error in errors)

    def test_optional_desc(self, valid_collection_data):
        valid_collection_data.pop('description')

        collection = DocumentCreate(**valid_collection_data)
        assert collection.description is None

    def test_missing_title(self, valid_collection_data):
        valid_collection_data.pop('title')

        with pytest.raises(ValidationError) as validation_err:
            DocumentCreate(**valid_collection_data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('title',) for error in errors)

    def test_min_valid_value(self):
        data = {
            'title': 'ABC'
        }

        collection = DocumentCreate(**data)

        assert collection.title == 'ABC'
        assert collection.description is None

    def test_title_special_chars(self, valid_collection_data):
        valid_collection_data['title'] = "Project: API & Database Setup (Phase 1)"

        collection = DocumentCreate(**valid_collection_data)
        assert collection.title == valid_collection_data['title']

    def test_empty_title(self, valid_collection_data):
        valid_collection_data['title'] = ''

        with pytest.raises(ValidationError) as validation_err:
            DocumentCreate(**valid_collection_data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('title',) for error in errors)

    def test_whitespace_title(self, valid_collection_data):
        valid_collection_data['title'] = ' '

        with pytest.raises(ValidationError) as validation_err:
            DocumentCreate(**valid_collection_data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('title',) for error in errors)

    def test_long_description(self, valid_collection_data):
        valid_collection_data['description'] = 'a' * 5000

        with pytest.raises(ValidationError) as validation_err:
            DocumentCreate(**valid_collection_data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('description',) for error in errors)

@pytest.mark.unit
@pytest.mark.taskapp
class TestDocumentUpdateModel:
    def test_valid_document_update(self, valid_collection_data):
        document = DocumentUpdate(**valid_collection_data)

        assert document.title == valid_collection_data['title']
        assert document.description == valid_collection_data['description']

    def test_partial_update_title(self, valid_collection_data):
        valid_collection_data.pop('description')
        collection = DocumentUpdate(**valid_collection_data)
        assert collection.title == valid_collection_data['title']

    def test_partial_update_desc(self, valid_collection_data):
        valid_collection_data.pop('title')
        collection = DocumentUpdate(**valid_collection_data)
        assert collection.description == valid_collection_data['description']

    def test_update_empty(self):
        with pytest.raises(ValidationError) as exc:
            DocumentUpdate()

        errors = exc.value.errors()

        assert len(errors) == 1
        assert errors[0]["type"] == "value_error"
        assert "Provide at least one field to update" in errors[0]["msg"]

    def test_update_title_short(self):
        data = {
            'title': ''
        }

        with pytest.raises(ValidationError) as validation_err:
            DocumentUpdate(**data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('title', ) for error in errors)

    def test_update_title_long(self):
        data = {
            'title': 'A' * 150
        }

        with pytest.raises(ValidationError) as validation_err:
            DocumentUpdate(**data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('title',) for error in errors)

    def test_update_none_val(self):
        data = {
            'title': None,
            'description': None
        }

        with pytest.raises(ValidationError) as exc:
            DocumentUpdate(**data)

        errors = exc.value.errors()

        assert len(errors) == 1
        assert errors[0]["type"] == "value_error"
        assert "Provide at least one field to update" in errors[0]["msg"]

@pytest.mark.unit
@pytest.mark.taskapp
class TestDocumentReadModel:
    def test_collection_read_from_dict(self, valid_collection_data):
        data = {
            'id': 1,
            **valid_collection_data,
            'created_at': datetime.now(),
            'updated_at': None
        }
        collection = DocumentRead(**data)

        assert collection.id == 1
        assert collection.title == valid_collection_data['title']

    def test_collection_read_orm(self, sample_collection_entity):
        collection = DocumentRead.model_validate(sample_collection_entity)

        assert collection.id == sample_collection_entity.id
        assert collection.title == sample_collection_entity.title
        assert collection.description == sample_collection_entity.description

    def test_collection_read_missing_id(self, valid_collection_data):
        with pytest.raises(ValidationError) as validation_err:
            DocumentRead(**valid_collection_data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('id', ) for error in errors)

    def test_collection_missing_title(self, valid_collection_data):
        valid_collection_data.update({'id': 1})
        valid_collection_data.pop('title')

        with pytest.raises(ValidationError) as validation_err:
            DocumentRead(**valid_collection_data)

        errors = validation_err.value.errors()
        assert any(error['loc'] == ('title',) for error in errors)

    def test_collection_read_updated_at(self, valid_collection_data):
        data = {
            'id': 1,
            **valid_collection_data,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        collection = DocumentRead(**data)
        assert collection.updated_at is not None