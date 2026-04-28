import pytest
from fastapi import status

from app.fileapp.exceptions import (
    DocumentNotFoundException,
    InvalidFileTypeException,
)
from app.fileapp.services.upload_service import FileUploadService


@pytest.mark.integration
@pytest.mark.fileapp
class TestUploadFileRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._url = "api/files/upload"

    def test_upload_success(self, client, auth_headers, mocker):
        mocker.patch.object(FileUploadService, "upload_file", return_value=None)

        response = client.post(
            self._url,
            files={"file": ("test.txt", b"hello content", "text/plain")},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "file upload successful"

    def test_upload_without_auth(self, client):
        response = client.post(
            self._url,
            files={"file": ("test.txt", b"hello content", "text/plain")},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_no_file_field_returns_422(self, client, auth_headers):
        response = client.post(self._url, data={}, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_upload_empty_filename_returns_error(self, client, auth_headers):
        # Empty filename fails FastAPI form validation before reaching the router
        response = client.post(
            self._url,
            files={"file": ("", b"content", "text/plain")},
            headers=auth_headers,
        )

        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    def test_upload_invalid_file_type_returns_400(self, client, auth_headers, mocker):
        mocker.patch.object(
            FileUploadService,
            "upload_file",
            side_effect=InvalidFileTypeException("file type mismatch or not allowed"),
        )

        response = client.post(
            self._url,
            files={"file": ("malware.exe", b"MZ\x90\x00", "application/x-dosexec")},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_document_not_found_returns_404(self, client, auth_headers, mocker):
        mocker.patch.object(
            FileUploadService,
            "upload_file",
            side_effect=DocumentNotFoundException("document_collection-99 does not exist"),
        )

        response = client.post(
            self._url,
            files={"file": ("test.txt", b"hello content", "text/plain")},
            data={"document_id": 99},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_with_document_id_success(self, client, auth_headers, mocker):
        mocker.patch.object(FileUploadService, "upload_file", return_value=None)

        response = client.post(
            self._url,
            files={"file": ("test.txt", b"hello content", "text/plain")},
            data={"document_id": 1},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_upload_response_structure(self, client, auth_headers, mocker):
        mocker.patch.object(FileUploadService, "upload_file", return_value=None)

        response = client.post(
            self._url,
            files={"file": ("test.txt", b"hello content", "text/plain")},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.json()
