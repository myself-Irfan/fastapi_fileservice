from datetime import timedelta

import pytest

from app.auth.exceptions import AuthenticationError
from app.auth.enums import TokenType
from app.auth.service import AuthenticationService


@pytest.mark.unit
class TestCreateJwtFailure:
    def test_encode_failure_does_not_leak_error_details(self, mocker):
        mocker.patch('app.auth.service.jwt.encode', side_effect=RuntimeError('secret internal detail'))

        with pytest.raises(AuthenticationError) as exc_info:
            AuthenticationService._create_jwt(1, timedelta(minutes=5), TokenType.ACCESS)

        assert exc_info.value.message == 'Failed to create access token'
