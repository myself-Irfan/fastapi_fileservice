import pytest
from faker import Faker

from app.taskapp.exceptions import CollectionNotFoundException
from app.taskapp.model import DocumentUpdate, DocumentCreate

fake = Faker()

@pytest.mark.unit
@pytest.mark.taskapp
class TestCollectionServiceIntegration:
    def test_create_fetch_collection(self, document_service, valid_collection_create):
        document_id = document_service.create_document(
            user_id=1,
            doc_col_data=valid_collection_create
        )
        assert document_id is not None

        fetched_doc = document_service.fetch_document_by_id(
            user_id=1,
            document_id=document_id
        )
        assert fetched_doc.id == document_id
        assert fetched_doc.title == valid_collection_create.title
        assert fetched_doc.description == valid_collection_create.description

    def test_update_verify_collection(self, document_service, make_test_document):
        updated_data = DocumentUpdate(
            title='updated_title',
            description='updated_description'
        )

        document_service.update_document(
            user_id=1,
            document_id=make_test_document.id,
            doc_col_data=updated_data
        )
        updated_collection = document_service.fetch_document_by_id(
            user_id=1,
            document_id=make_test_document.id
        )

        assert updated_collection.title == updated_data.title
        assert updated_collection.description == updated_data.description

    def test_delete_verify_collection(self, document_service, make_test_user, make_test_document):
        document_service.delete_collection(
            user_id=make_test_user.id,
            collection_id=make_test_document.id
        )

        with pytest.raises(CollectionNotFoundException):
            document_service.fetch_document_by_id(
                user_id=make_test_user.id,
                document_id=make_test_document.id
            )

    def test_fetch_multiple_collections(self, document_service, make_test_user):
        #todo: include user_id if read model will change user_id
        for i in range(3):
            data : dict = {
                'title': fake.sentence(nb_words=5),
                'description': fake.text(max_nb_chars=200)
            }
            document_service.create_document(
                user_id=make_test_user.id,
                doc_col_data=DocumentCreate(**data)
            )

        collections = document_service.fetch_documents(user_id=make_test_user.id)

        assert len(collections) >= 3

    def test_user_data_isolation(self, document_service):
        doc_id_u1 = document_service.create_document(
            user_id=1,
            doc_col_data=DocumentCreate(
                title=fake.sentence(nb_words=5),
                description=fake.text(max_nb_chars=200)
            )
        )
        doc_id_u2 = document_service.create_document(
            user_id=2,
            doc_col_data=DocumentCreate(
                title=fake.sentence(nb_words=5),
                description=fake.text(max_nb_chars=200)
            )
        )

        with pytest.raises(CollectionNotFoundException):
            document_service.fetch_document_by_id(
                user_id=1,
                document_id=doc_id_u2
            )
        with pytest.raises(CollectionNotFoundException):
            document_service.fetch_document_by_id(
                user_id=2,
                document_id=doc_id_u1
            )