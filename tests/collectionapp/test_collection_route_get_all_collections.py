import pytest
from fastapi import status

from tests.collectionapp.conftest import document_service


@pytest.mark.integration
@pytest.mark.taskapp
class TestGetAllCollectionsRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._get_all_url = 'api/tasks/'

    def test_get_all_collections_success(self, client, auth_headers, make_test_collection):
        response = client.get(self._get_all_url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)

    def test_get_all_collections_without_auth(self, client):
        response = client.get(self._get_all_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_all_collections_empty_list(self, client, auth_headers):
        response = client.get(self._get_all_url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_all_collections_responses_structure(self, client, auth_headers, make_test_collection):
        response = client.get(self._get_all_url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert "data" in data

        if len(data["data"]) > 0:
            collection = data["data"][0]
            assert "id" in collection
            assert "title" in collection
            assert "description" in collection
            assert "created_at" in collection
            assert "updated_at" in collection

    def test_get_all_documents_message_format(self, client, auth_headers):
        response = client.get(self._get_all_url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        message = response.json()["message"]

        assert "retrieved successfully" in message.lower() or "no collection" in message.lower()
