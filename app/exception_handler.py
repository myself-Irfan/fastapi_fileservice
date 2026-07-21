from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.exceptions import AppException
from app.logger import get_logger

logger = get_logger(__name__)


class AppExceptionHandler:
    """Global handler for AppException and its subclasses."""

    @staticmethod
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "Application exception",
            path=request.url.path,
            status_code=exc.status_code,
            error=exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    @staticmethod
    async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled exception",
            path=request.url.path,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )