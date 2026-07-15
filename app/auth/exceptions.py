from fastapi import status

from app.exceptions import AppException


class AuthenticationError(AppException):
    """Custom exception for authentication errors."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)
