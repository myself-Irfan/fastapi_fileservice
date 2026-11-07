import pytest
from argon2.exceptions import HashingError

from app.auth.exceptions import AuthenticationError
from app.auth.hashing import hash_pwd


@pytest.mark.unit
class TestHashPwdFailure:
    def test_hashing_failure_propagates_as_server_error(self, mocker):
        hasher = mocker.patch('app.auth.hashing._pwd_hasher')
        hasher.hash.side_effect = HashingError('secret internal detail')

        with pytest.raises(HashingError) as exc_info:
            hash_pwd('password123')

        assert not isinstance(exc_info.value, AuthenticationError)
