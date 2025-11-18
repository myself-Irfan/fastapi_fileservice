import pytest
from faker import Faker
from datetime import datetime
from sqlalchemy.orm import Session

from app.taskapp.entities import DocumentCollection
from app.taskapp.service import DocumentService
from app.taskapp.model import DocumentCreate, DocumentUpdate


fake = Faker()

@pytest.fixture
def document_service(db_session):
    return DocumentService(db=db_session)

@pytest.fixture
def mock_document_service(mock_db_session):
    return DocumentService(db=mock_db_session)

@pytest.fixture
def valid_collection_data():
    return {
        'title': fake.sentence(nb_words=5),
        'description': fake.text(max_nb_chars=200)
    }

@pytest.fixture
def valid_collection_create(valid_collection_data):
    return DocumentCreate(**valid_collection_data)

@pytest.fixture
def valid_collection_update(valid_collection_data):
    return DocumentUpdate(**valid_collection_data)

@pytest.fixture
def sample_collection_entity(valid_collection_data, make_test_user):
    return DocumentCollection(
        id=1,
        user_id=make_test_user.id,
        title=valid_collection_data['title'],
        description=valid_collection_data['description'],
        is_active=True,
        created_at=datetime.now()
    )

@pytest.fixture
def multiple_collection_entity(make_test_user):
    return [
        DocumentCollection(
            id=1,
            user_id=make_test_user.id,
            title=f'Test Doc - {i}',
            description=fake.text(max_nb_chars=20),
            created_at=datetime.now()
        )
        for i in range(4)
    ]

@pytest.fixture(scope='session')
def make_test_document(db_engine, valid_collection_data, make_test_user):
    with Session(bind=db_engine) as session:
        collection = DocumentCollection(
            user_id=make_test_user.id,
            title=valid_collection_data['title'],
            description=valid_collection_data['description']
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)

    return collection