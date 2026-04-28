import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.fileapp
class TestDeleteFileRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._url = "api/files/{file_id}"

    def test_delete_file_success(self, client, auth_headers, make_test_file):
        url = self._url.format(file_id=make_test_file.id)
        response = client.delete(url, headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.text == ""

    def test_delete_file_not_found(self, client, auth_headers):
        url = self._url.format(file_id=999999)
        response = client.delete(url, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_delete_file_without_auth(self, client, make_test_file):
        url = self._url.format(file_id=make_test_file.id)
        response = client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_file_invalid_id_type(self, client, auth_headers):
        response = client.delete("api/files/invalid_id", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_file_twice_second_returns_404(self, client, auth_headers, make_test_file):
        url = self._url.format(file_id=make_test_file.id)

        first = client.delete(url, headers=auth_headers)
        assert first.status_code == status.HTTP_204_NO_CONTENT

        second = client.delete(url, headers=auth_headers)
        assert second.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_file_verify_no_longer_accessible(self, client, auth_headers, make_test_file):
        url = self._url.format(file_id=make_test_file.id)
        client.delete(url, headers=auth_headers)

        get_resp = client.get(url, headers=auth_headers)
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND
