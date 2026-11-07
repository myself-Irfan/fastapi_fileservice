from typing import Callable, TypeVar

from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session

from app.exceptions import AppException
from app.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def get_or_raise(
    db: Session,
    model: type[T],
    resource_id: int | None,
    label: str,
    not_found: Callable[[str], AppException],
    on_error: Callable[[str], AppException],
    **filters,
) -> T:
    """Fetches `model` by id (narrowed by `filters`), translating SQLAlchemy errors into `on_error` and a missing row into `not_found`."""
    log_context = {f"{label}_id": resource_id}
    try:
        instance = db.query(model).filter_by(id=resource_id, **filters).first()
    except (SQLAlchemyError, OperationalError) as db_err:
        logger.error(f"{label} retrieval failed", error=db_err, exc_info=True, **log_context)
        raise on_error(f"database error while retrieving {label}-{resource_id}") from db_err

    if instance is None:
        logger.warning(f"{label} not found", **log_context)
        raise not_found(f"{label}-{resource_id} not found")
    return instance
