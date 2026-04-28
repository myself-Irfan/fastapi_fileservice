import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.fileapp
class TestGetFileByIdRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._url = "api/files/{file_id}"

    def test_get_file_success(self, client, auth_headers, make_test_file):
        url = self._url.format(file_id=make_test_file.id)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["id"] == make_test_file.id
        assert data["data"]["title"] == make_test_file.title

    def test_get_file_not_found(self, client, auth_headers):
        url = self._url.format(file_id=999999)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_file_without_auth(self, client, make_test_file):
        url = self._url.format(file_id=make_test_file.id)
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_file_invalid_id_type(self, client, auth_headers):
        response = client.get("api/files/not_an_int", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_file_response_structure(self, client, auth_headers, make_test_file):
        url = self._url.format(file_id=make_test_file.id)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "data" in data

        file = data["data"]
        for field in ("id", "title", "is_active", "file_path", "file_size", "mime_type", "extension", "created_at"):
            assert field in file

    def test_get_file_returns_correct_metadata(self, client, auth_headers, make_test_file):
        url = self._url.format(file_id=make_test_file.id)
        response = client.get(url, headers=auth_headers)

        file = response.json()["data"]
        assert file["mime_type"] == make_test_file.mime_type
        assert file["extension"] == make_test_file.extension
        assert file["file_size"] == make_test_file.file_size
        assert file["is_active"] is True
