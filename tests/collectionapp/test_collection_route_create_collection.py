import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.userapp
class TestCreateCollectionRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._create_url = 'api/tasks/'

    def test_create_collection_success(self, client, valid_collection_data, auth_headers):
        response = client.post(
            self._create_url,
            json=valid_collection_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert 'message' in response.json()
        assert "created successfully" in response.json()["message"].lower()

    def test_create_collection_without_auth(self, client, valid_collection_data):
        response = client.post(
            self._create_url,
            json=valid_collection_data,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_collection_minimal_data(self, client, auth_headers):
        minimal_data = {"title": "Minimal Document"}

        response = client.post(
            self._create_url,
            json=minimal_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_document_missing_title(self, client, valid_collection_data, auth_headers):
        valid_collection_data.pop('title')
        response = client.post(self._create_url, json=valid_collection_data, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_document_empty_payload(self, client, auth_headers):
        response = client.post(self._create_url, json={}, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_document_title_too_long(self, client, auth_headers):
        data = {"title": "a" * 150}
        response = client.post(self._create_url, json=data, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_document_with_special_chars(self, client, auth_headers):
        data = {
            "title": "Project: API & Database Setup (Phase 1)",
            "description": "Setup API endpoints & database models"
        }
        response = client.post(self._create_url, json=data, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_document_empty_title(self, client, auth_headers):
        data = {"title": ""}
        response = client.post(self._create_url, json=data, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_document_whitespace_title(self, client, auth_headers):
        data = {"title": "   "}
        response = client.post(self._create_url, json=data, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY