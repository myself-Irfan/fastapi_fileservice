from fastapi import status

from app.exceptions import AppException

class UserOperationException(AppException):
    """
    base exception for user op (registration, login, auth)
    """
    pass

class UserDuplicateException(UserOperationException):
    """
    user with the given email already exists
    """
    def __init__(self, message: str = 'email already in use'):
        super().__init__(message)

class InvalidCredentialsException(UserOperationException):
    """
    invalid login creds provided
    """
    def __init__(self, message: str = 'invalid credentials'):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)

class UserCreationException(UserOperationException):
    """
    User creation failed
    """
    def __init__(self, message: str = "Failed to create user"):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatabaseOperationException(UserOperationException):
    """
    Database operation failed
    """
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

