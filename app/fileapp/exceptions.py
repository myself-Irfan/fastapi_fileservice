from fastapi import status

from app.exceptions import AppException


class FileOperationException(AppException):
    """
    base exception for file operations (read, download, delete)
    """
    pass

class FileNotFoundException(FileOperationException):
    """
    file not found
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class FileDeletionException(FileOperationException):
    """
    file deletion fails
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FileUploadException(AppException):
    """
    base exception class for file upload operations
    """
    pass

class DocumentNotFoundException(FileUploadException):
    """
    document collection does not exist
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class InvalidFileTypeException(FileUploadException):
    """
    file type validation fails
    """
    def __init__(self, message: str):
        super().__init__(message)

class FileProcessingException(FileUploadException):
    """
    file processing failed
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)