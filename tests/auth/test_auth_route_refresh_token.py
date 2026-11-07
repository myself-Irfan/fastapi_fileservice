import pytest
from fastapi import status

from app.auth.service import AuthenticationService
from tests.userapp.conftest import make_test_user


REFRESH_URL = 'api/auth/refresh-token'


@pytest.mark.integration
class TestRefreshTokenRoute:
    def test_valid_refresh_token_returns_new_access_token(self, client, make_test_user):
        token = AuthenticationService.generate_refresh_token(make_test_user.id)
        response = client.post(REFRESH_URL, headers={'Authorization': f'Bearer {token}'})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['data']['access_token']

    def test_bad_header_format_returns_401_with_www_authenticate(self, client):
        response = client.post(REFRESH_URL, headers={'Authorization': 'Token abc'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Invalid Authorization header format'}
        assert response.headers['www-authenticate'] == 'Bearer'

    def test_invalid_refresh_token_returns_401_with_www_authenticate(self, client):
        response = client.post(REFRESH_URL, headers={'Authorization': 'Bearer junk'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Invalid refresh token'}
        assert response.headers['www-authenticate'] == 'Bearer'
