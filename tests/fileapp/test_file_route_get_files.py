import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.fileapp
class TestGetAllFilesRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._url = "api/files/"

    def test_get_all_files_success(self, client, auth_headers, make_test_file):
        response = client.get(self._url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_all_files_without_auth(self, client):
        response = client.get(self._url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_all_files_empty_returns_200(self, client, auth_headers):
        response = client.get(self._url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json()["data"], list)

    def test_get_all_files_response_structure(self, client, auth_headers, make_test_file):
        response = client.get(self._url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "data" in data

        if len(data["data"]) > 0:
            file = data["data"][0]
            for field in ("id", "title", "is_active", "file_size", "mime_type", "extension", "created_at"):
                assert field in file

    def test_get_all_files_message_format(self, client, auth_headers, make_test_file):
        response = client.get(self._url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        message = response.json()["message"]
        assert "success" in message.lower() or "retrieve" in message.lower() or "no files" in message.lower()

    def test_get_all_files_with_document_id_filter(self, client, auth_headers):
        response = client.get(self._url, params={"document_id": 9999}, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == []
