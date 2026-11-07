from unittest.mock import Mock

import pytest
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

from app.auth.dependencies import get_current_user
from app.auth.exceptions import AuthenticationError
from app.auth.service import AuthenticationService
from app.exceptions import AppException
from tests.userapp.conftest import make_test_user


PROTECTED_URL = 'api/collection/'


@pytest.mark.integration
class TestGetCurrentUserRoute:
    def test_valid_access_token_is_accepted(self, client, make_test_user):
        token = AuthenticationService.generate_access_token(make_test_user.id)
        response = client.get(PROTECTED_URL, headers={'Authorization': f'Bearer {token}'})

        assert response.status_code == status.HTTP_200_OK

    def test_invalid_token_returns_401_with_www_authenticate(self, client):
        response = client.get(PROTECTED_URL, headers={'Authorization': 'Bearer junk'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Invalid/expired token'}
        assert response.headers['www-authenticate'] == 'Bearer'

    def test_refresh_token_used_as_access_returns_401(self, client, make_test_user):
        token = AuthenticationService.generate_refresh_token(make_test_user.id)
        response = client.get(PROTECTED_URL, headers={'Authorization': f'Bearer {token}'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.headers['www-authenticate'] == 'Bearer'

    def test_token_for_missing_user_returns_401_with_www_authenticate(self, client):
        token = AuthenticationService.generate_access_token(999999)
        response = client.get(PROTECTED_URL, headers={'Authorization': f'Bearer {token}'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'User-999999 not found'}
        assert response.headers['www-authenticate'] == 'Bearer'


@pytest.mark.unit
class TestGetCurrentUserDbError:
    def test_db_error_raises_500_app_exception(self, mocker):
        mocker.patch.object(AuthenticationService, 'get_user_from_token', return_value=1)
        db = Mock()
        db.get.side_effect = SQLAlchemyError('secret internal detail')

        with pytest.raises(AppException) as exc_info:
            get_current_user('token', db)

        assert not isinstance(exc_info.value, AuthenticationError)
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.message == 'Database error'
