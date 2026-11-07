import pytest
from argon2.exceptions import HashingError

from app.auth.exceptions import AuthenticationError
from app.auth.hashing import hash_pwd


@pytest.mark.unit
class TestHashPwdFailure:
    def test_hashing_failure_does_not_leak_error_details(self, mocker):
        hasher = mocker.patch('app.auth.hashing._pwd_hasher')
        hasher.hash.side_effect = HashingError('secret internal detail')

        with pytest.raises(AuthenticationError) as exc_info:
            hash_pwd('password123')

        assert exc_info.value.message == 'Password hashing failed'
