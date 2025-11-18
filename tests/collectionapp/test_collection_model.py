import pytest
from pydantic import ValidationError

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