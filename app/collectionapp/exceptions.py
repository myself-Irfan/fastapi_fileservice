from fastapi import status

from app.exceptions import AppException


class CollectionOperationException(AppException):
    pass

class CollectionNotFoundException(CollectionOperationException):
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)