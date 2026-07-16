from argon2 import PasswordHasher
from argon2.exceptions import HashingError, InvalidHashError, VerifyMismatchError

from app.auth.exceptions import AuthenticationError
from app.logger import get_logger

logger = get_logger(__name__)

_pwd_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


def hash_pwd(pwd_str: str) -> str:
    """
    Hash a password using argon2.
    :param pwd_str: Plain text password
    :return: Hashed password string
    :raises ValueError: If password is empty
    :raises AuthenticationError: If hashing fails
    """
    if not pwd_str or not pwd_str.strip():
        raise ValueError('Password cannot be empty')

    try:
        return _pwd_hasher.hash(pwd_str)
    except HashingError as err:
        logger.error(f'Password hashing failed: {err}')
        raise AuthenticationError(f'Password hashing failed: {err}') from err


def verify_pwd(pwd_hashed: str, pwd_str: str) -> tuple[bool, bool]:
    """
    Verify password and check if rehash is needed.
    :param pwd_hashed: Hashed password from database
    :param pwd_str: Plain text password
    :return: (is_valid, needs_rehash)
    """
    try:
        if _pwd_hasher.verify(pwd_hashed, pwd_str):
            need_rehash = _pwd_hasher.check_needs_rehash(pwd_hashed)
            if need_rehash:
                logger.info('Password needs rehash')
            return True, need_rehash
    except VerifyMismatchError as ver_err:
        logger.warning(f'Verify mismatch error: {ver_err}')
    except InvalidHashError as invalid_err:
        logger.error(f'Invalid hash error: {invalid_err}')
    except Exception as err:
        logger.error(f'Unexpected error: {err}')

    return False, False
