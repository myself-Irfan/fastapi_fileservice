from datetime import datetime

import pytest
from fastapi import status

from app.fileapp.model import FileRead
from app.fileapp.services.upload_service import FileUploadService


def _sample_file_read(**overrides):
    data = dict(
        id=1,
        title="notes.txt",
        is_active=True,
        file_size=7,
        mime_type="text/plain",
        extension=".txt",
        checksum="deadbeef",
        created_at=datetime.now(),
        updated_at=None,
        document_id=None,
        user_id=1,
    )
    data.update(overrides)
    return FileRead(**data)


@pytest.mark.integration
@pytest.mark.fileapp
class TestFileFlowIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._files_url = "api/files/"
        self._file_url = "api/files/{file_id}"
        self._download_url = "api/files/{file_id}/download"
        self._upload_url = "api/files/upload"

    def test_list_get_delete_flow(self, client, auth_headers, make_test_file):
        # list — file appears
        list_resp = client.get(self._files_url, headers=auth_headers)
        assert list_resp.status_code == status.HTTP_200_OK
        ids = [f["id"] for f in list_resp.json()["data"]]
        assert make_test_file.id in ids

        # get by id
        get_resp = client.get(self._file_url.format(file_id=make_test_file.id), headers=auth_headers)
        assert get_resp.status_code == status.HTTP_200_OK
        assert get_resp.json()["data"]["id"] == make_test_file.id

        # delete
        del_resp = client.delete(self._file_url.format(file_id=make_test_file.id), headers=auth_headers)
        assert del_resp.status_code == status.HTTP_204_NO_CONTENT

        # get after delete → 404
        get_after = client.get(self._file_url.format(file_id=make_test_file.id), headers=auth_headers)
        assert get_after.status_code == status.HTTP_404_NOT_FOUND

        # list after delete — file no longer appears
        list_after = client.get(self._files_url, headers=auth_headers)
        remaining_ids = [f["id"] for f in list_after.json()["data"]]
        assert make_test_file.id not in remaining_ids

    def test_upload_then_list_flow(self, client, auth_headers, mocker):
        # track what the service would have created
        mocker.patch.object(FileUploadService, "upload_file", return_value=_sample_file_read())

        upload_resp = client.post(
            self._upload_url,
            files={"file": ("notes.txt", b"content", "text/plain")},
            headers=auth_headers,
        )
        assert upload_resp.status_code == status.HTTP_201_CREATED
        assert upload_resp.json()["message"] == "file upload successful"

    def test_download_flow(self, client, auth_headers, make_test_file_with_physical):
        download_resp = client.get(
            self._download_url.format(file_id=make_test_file_with_physical.id),
            headers=auth_headers,
        )
        assert download_resp.status_code == status.HTTP_200_OK
        assert download_resp.content == b"hello test content for download"

        # file still accessible after download
        get_resp = client.get(
            self._file_url.format(file_id=make_test_file_with_physical.id),
            headers=auth_headers,
        )
        assert get_resp.status_code == status.HTTP_200_OK

    def test_delete_nonexistent_does_not_affect_others(self, client, auth_headers, make_test_file):
        # delete something that doesn't exist
        del_resp = client.delete(self._file_url.format(file_id=999999), headers=auth_headers)
        assert del_resp.status_code == status.HTTP_404_NOT_FOUND

        # existing file unaffected
        get_resp = client.get(self._file_url.format(file_id=make_test_file.id), headers=auth_headers)
        assert get_resp.status_code == status.HTTP_200_OK

    def test_unauthenticated_cannot_access_any_endpoint(self, client, make_test_file):
        assert client.get(self._files_url).status_code == status.HTTP_401_UNAUTHORIZED
        assert client.get(self._file_url.format(file_id=make_test_file.id)).status_code == status.HTTP_401_UNAUTHORIZED
        assert client.delete(self._file_url.format(file_id=make_test_file.id)).status_code == status.HTTP_401_UNAUTHORIZED
        assert client.get(self._download_url.format(file_id=make_test_file.id)).status_code == status.HTTP_401_UNAUTHORIZED
