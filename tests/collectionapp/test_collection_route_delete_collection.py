import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.taskapp
class TestDeleteCollectionRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._create_url = 'api/tasks/'
        self._delete_url = 'api/tasks/{collection_id}'
        self._get_url = 'api/tasks/{collection_id}'

    def test_delete_collection_success(self, client, auth_headers, make_test_collection):
        url = self._delete_url.format(collection_id=make_test_collection.id)
        response = client.delete(url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.json()
        assert 'deleted successfully' in response.json()['message'].lower()

    def test_delete_collection_not_found(self, client, auth_headers):
        url = self._delete_url.format(collection_id=999)
        response = client.delete(url, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'not found' in response.json()["detail"].lower()

    def test_delete_collection_twice(self, client, auth_headers, make_test_collection):
        url = self._delete_url.format(collection_id=make_test_collection.id)

        response = client.delete(url, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        response = client.delete(url, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_collection_verify_removed(self, client, auth_headers, make_test_collection):
        client.delete(
            self._delete_url.format(collection_id=make_test_collection.id),
            headers=auth_headers
        )

        get_resp = client.get(
            self._get_url.format(collection_id=make_test_collection.id),
            headers=auth_headers
        )
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_document_invalid_id_type(self, client, auth_headers):
        url = 'api/tasks/invalid_id'
        response = client.delete(url, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY