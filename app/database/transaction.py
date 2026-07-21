from contextlib import contextmanager
from typing import Callable, Iterator, Sequence

from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session

from app.exceptions import AppException
from app.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def db_transaction(
    db: Session,
    on_error: Callable[[str], AppException],
    message: str,
    refresh: Sequence[object] = (),
    **log_context,
) -> Iterator[None]:
    """Commits `db` on success (refreshing `refresh`), rolls back and translates SQLAlchemy errors into a domain AppException on failure."""
    try:
        yield
        db.commit()
        for obj in refresh:
            db.refresh(obj)
    except (SQLAlchemyError, OperationalError) as db_err:
        db.rollback()
        logger.error(message, error=db_err, exc_info=True, **log_context)
        raise on_error(message) from db_err
