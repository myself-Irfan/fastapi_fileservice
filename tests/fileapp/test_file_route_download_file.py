import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.fileapp
class TestDownloadFileRoute:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._url = "api/files/{file_id}/download"

    def test_download_success(self, client, auth_headers, make_test_file_with_physical):
        url = self._url.format(file_id=make_test_file_with_physical.id)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.content == b"hello test content for download"

    def test_download_not_found(self, client, auth_headers):
        url = self._url.format(file_id=999999)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_download_without_auth(self, client, make_test_file_with_physical):
        url = self._url.format(file_id=make_test_file_with_physical.id)
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_download_invalid_id_type(self, client, auth_headers):
        response = client.get("api/files/not_an_int/download", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_download_returns_correct_content_type(
        self, client, auth_headers, make_test_file_with_physical
    ):
        url = self._url.format(file_id=make_test_file_with_physical.id)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "text/plain" in response.headers["content-type"]

    def test_download_physical_file_missing_returns_404(
        self, client, auth_headers, make_test_file
    ):
        # make_test_file points to a nonexistent physical path
        url = self._url.format(file_id=make_test_file.id)
        response = client.get(url, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
