from fastapi import status


class CollectionOperationException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message: str = message
        self.status_code: int = status_code
        super().__init__(self.message)

class CollectionNotFoundException(CollectionOperationException):
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)