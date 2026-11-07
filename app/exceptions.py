from fastapi import status


class AppException(Exception):
    """Base exception for all domain-specific application errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, headers: dict[str, str] | None = None):
        self.message: str = message
        self.status_code: int = status_code
        self.headers: dict[str, str] | None = headers
        super().__init__(self.message)