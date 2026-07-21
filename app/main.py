from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.middleware.logging_context import LoggingContextMiddleware
from app.validation_handler import ValidationErrorHandler
from app.exceptions import AppException
from app.exception_handler import AppExceptionHandler
from app.logger import configure_logger
from app.routers import register_routers


def create_app() -> FastAPI:
    configure_logger()

    app = FastAPI(
        title='File Service App',
        description='A file management App with JWT',
        version='1.0.0',
        docs_url='/docs',
        redoc_url='/redoc'
    )

    app.add_middleware(LoggingContextMiddleware)

    app.add_exception_handler(
        RequestValidationError,
        ValidationErrorHandler.handle_validation_error
    )

    app.add_exception_handler(
        AppException,
        AppExceptionHandler.handle_app_exception
    )

    app.add_exception_handler(
        Exception,
        AppExceptionHandler.handle_unhandled_exception
    )

    app.mount('/static', StaticFiles(directory='static'), name='static')

    register_routers(app)

    return app

app = create_app()


# TODO: log request response to table
# TODO: crontab to remind users for missed task
# TODO: add pagination for get list APIs
# TODO: add file count for doc_collection
# TODO: should we add user_id to DocumentRead?
# TODO: update test to register class-wise and cleanup instead of test-wise | rewrite whole test