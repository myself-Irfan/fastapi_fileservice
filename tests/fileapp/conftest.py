import uuid
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.fileapp.entities import DocumentCollectionFile
from app.fileapp.services.base_service import FileService
from tests.userapp.conftest import make_test_user


@pytest.fixture
def file_service(db_session):
    return FileService(db=db_session)


@pytest.fixture
def mock_file_service(mock_db_session):
    return FileService(db=mock_db_session)


@pytest.fixture
def sample_file_entity(make_test_user):
    return DocumentCollectionFile(
        id=1,
        title="test_file.pdf",
        is_active=True,
        file_path="/uploads/deadbeef.pdf",
        file_size=1024,
        mime_type="application/pdf",
        extension=".pdf",
        checksum="a" * 64,
        created_at=datetime.now(),
        updated_at=None,
        document_id=None,
        user_id=make_test_user.id,
    )


@pytest.fixture
def multiple_file_entities(make_test_user):
    return [
        DocumentCollectionFile(
            id=i,
            title=f"file_{i}.txt",
            is_active=True,
            file_path=f"/uploads/{'0' * 60}{i:04d}.txt",
            file_size=512 * i,
            mime_type="text/plain",
            extension=".txt",
            checksum=f"{i:064d}",
            created_at=datetime.now(),
            updated_at=None,
            document_id=None,
            user_id=make_test_user.id,
        )
        for i in range(1, 4)
    ]


@pytest.fixture(scope="function")
def make_test_file(db_engine, make_test_user):
    checksum = (uuid.uuid4().hex * 2)[:64]
    with Session(bind=db_engine) as session:
        file_record = DocumentCollectionFile(
            title="integration_test_file.txt",
            is_active=True,
            file_path="/tmp/nonexistent_integration_test.txt",
            file_size=256,
            mime_type="text/plain",
            extension=".txt",
            checksum=checksum,
            user_id=make_test_user.id,
            document_id=None,
        )
        session.add(file_record)
        session.commit()
        session.refresh(file_record)
    return file_record


@pytest.fixture(scope="function")
def make_test_file_with_physical(db_engine, make_test_user, tmp_path):
    physical_file = tmp_path / "downloadable.txt"
    physical_file.write_text("hello test content for download")
    checksum = (uuid.uuid4().hex * 2)[:64]

    with Session(bind=db_engine) as session:
        file_record = DocumentCollectionFile(
            title="downloadable.txt",
            is_active=True,
            file_path=str(physical_file),
            file_size=physical_file.stat().st_size,
            mime_type="text/plain",
            extension=".txt",
            checksum=checksum,
            user_id=make_test_user.id,
            document_id=None,
        )
        session.add(file_record)
        session.commit()
        session.refresh(file_record)
    return file_record


@pytest.fixture
def auth_headers(client, make_test_user):
    client.app.dependency_overrides[get_current_user] = lambda: make_test_user
    return {"Authorization": "Bearer mock_token"}
