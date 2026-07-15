from fastapi import status


class AppException(Exception):
    """Base exception for all domain-specific application errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message: str = message
        self.status_code: int = status_code
        super().__init__(self.message)