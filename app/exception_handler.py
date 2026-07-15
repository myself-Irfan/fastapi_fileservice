from fastapi import Request
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