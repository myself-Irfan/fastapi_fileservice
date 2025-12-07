import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.taskapp
class TestGetCollectionIdRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._get_id_url = 'api/tasks/{collection_id}'

    def test_get_collection_id_success(self, client, auth_headers, make_test_collection):
        url = self._get_id_url.format(collection_id=make_test_collection.id)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        assert "data" in response.json()
        assert response.json()["data"]["id"] == make_test_collection.id

    def test_get_collection_by_id_not_found(self, client, auth_headers):
        url = self._get_id_url.format(collection_id=99999)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_collection_by_id_without_auth(self, client, make_test_collection):
        url = self._get_id_url.format(collection_id=make_test_collection.id)
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_collection_by_id_response_structure(self, client, auth_headers, make_test_collection):
        url = self._get_id_url.format(collection_id=make_test_collection.id)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert "data" in data

        assert "id" in data["data"]
        assert "title" in data["data"]
        assert "description" in data["data"]
        assert "created_at" in data["data"]
        assert "updated_at" in data["data"]

    def test_get_collection_verify_data(self, client, auth_headers, make_test_collection):
        url = self._get_id_url.format(collection_id=make_test_collection.id)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        doc_data = response.json()["data"]

        assert doc_data["title"] == make_test_collection.title
        assert doc_data["description"] == make_test_collection.description

    def test_get_document_invalid_id_type(self, client, auth_headers):
        url = self._get_id_url.format(collection_id='invalid_id')
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
