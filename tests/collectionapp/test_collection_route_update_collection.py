import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.taskapp
class TestUpdateCollectionRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._update_url = 'api/tasks/{collection_id}'
        self._create_url = 'api/tasks/'

    def test_update_collection_success(self, client, auth_headers, make_test_collection):
        url = self._update_url.format(collection_id=make_test_collection.id)
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        response = client.put(url, json=update_data, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        assert "updated successfully" in response.json()["message"].lower()

    def test_update_collection_partial_title(self, client, auth_headers, make_test_collection):
        url = self._update_url.format(collection_id=make_test_collection.id)
        update_data = {"title": "Only Title Update"}
        response = client.put(url, json=update_data, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

    def test_update_collection_partial_description(self, client, auth_headers, make_test_collection):
        url = self._update_url.format(collection_id=make_test_collection.id)
        update_data = {"description": "Only description update"}
        response = client.put(url, json=update_data, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

    def test_update_collection_not_found(self, client, auth_headers, valid_collection_data):
        url = self._update_url.format(collection_id=999)
        update_data = valid_collection_data
        response = client.put(
            url,
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_collection_no_auth(self, client, make_test_collection, valid_collection_data):
        url = self._update_url.format(collection_id=make_test_collection.id)
        update_data = valid_collection_data
        response = client.put(
            url,
            json=update_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_collection_empty_payload(self, client, auth_headers, make_test_collection):
        url = self._update_url.format(collection_id=make_test_collection.id)
        response = client.put(url, json={}, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"] == 'Validation error'
        assert "Invalid value" in response.json()["errors"][0]

    def test_update_collection_title_too_long(self, client, auth_headers, make_test_collection):
        url = self._update_url.format(collection_id=make_test_collection.id)
        update_data = {"title": "a" * 150}
        response = client.put(url, json=update_data, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_collection_preserve_others(self, client, auth_headers, make_test_collection):
        url = self._update_url.format(collection_id=make_test_collection.id)
        update_data = {"title": "updated_title"}
        client.put(
            url,
            json=update_data,
            headers=auth_headers
        )

        get_resp = client.get(
            url,
            headers=auth_headers
        )
        assert get_resp.json()["data"]["title"] == update_data.get("title")
        assert get_resp.json()["data"]["description"] == make_test_collection.description