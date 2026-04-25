import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.collectionapp
class TestCollectionFlowIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._base_url = 'api/collection'
        self._query_param_url = self._base_url + '/{collection_id}'

    def test_complete_crud_flow(self, client, auth_headers, valid_collection_data):
        # create
        create_resp = client.post(
            self._base_url,
            json=valid_collection_data,
            headers=auth_headers
        )
        assert create_resp.status_code == status.HTTP_201_CREATED

        col_id = create_resp.json()['id']

        # get
        get_resp = client.get(
            self._query_param_url.format(collection_id=col_id),
            headers=auth_headers
        )
        assert get_resp.status_code == status.HTTP_200_OK
        assert get_resp.json()['data']['title'] == valid_collection_data.get('title')

        # update
        update_data = {"title": "Updated Title", "description": "Updated description"}
        update_resp = client.put(
            self._query_param_url.format(collection_id=col_id),
            headers=auth_headers,
            json=update_data
        )
        assert update_resp.status_code == status.HTTP_200_OK

        get_resp = client.get(
            self._query_param_url.format(collection_id=col_id),
            headers=auth_headers
        )
        assert get_resp.status_code == status.HTTP_200_OK
        assert get_resp.json()['data']['title'] == update_data.get('title')
        assert get_resp.json()['data']['description'] == update_data.get('description')

        # delete
        delete_resp = client.delete(
            self._query_param_url.format(collection_id=col_id),
            headers=auth_headers
        )
        assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

        get_resp = client.get(
            self._query_param_url.format(collection_id=col_id),
            headers=auth_headers
        )
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_create_multiple_collection(self, client, auth_headers):
        collection_list = [
            {'title': "Col-1", 'description': 'first collection'},
            {'title': "Col-2", 'description': 'second collection'},
            {'title': "Col-3", 'description': 'third collection'},
        ]

        for col in collection_list:
            response = client.post(
                self._base_url,
                json=col,
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_201_CREATED

        get_all_response = client.get(
            self._base_url,
            headers=auth_headers
        )
        assert get_all_response.status_code == status.HTTP_200_OK
        assert len(get_all_response.json()['data']) == 3