import math
import time

from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.exceptions import AppException
from app.logger import get_logger
from app.rate_limiter import limiter

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
    async def handle_rate_limit_exceeded(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        rate_limit, keys = request.state.view_rate_limit
        reset_at, _ = limiter.limiter.get_window_stats(rate_limit, *keys)
        retry_after = max(1, math.ceil(reset_at - time.time()))

        logger.warning(
            "Rate limit exceeded",
            path=request.url.path,
            limit=str(rate_limit),
            retry_after=retry_after,
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests. Please try again later."},
            headers={"Retry-After": str(retry_after)},
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