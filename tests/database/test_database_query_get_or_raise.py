from functools import partial
from unittest.mock import Mock

import pytest
from fastapi import status
from sqlalchemy.exc import OperationalError

from app.database.query import get_or_raise
from app.exceptions import AppException


class NotFound(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


on_error = partial(AppException, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
Model = object()


def _fetch(db, **filters):
    return get_or_raise(db, Model, 7, "thing", not_found=NotFound, on_error=on_error, **filters)


@pytest.mark.unit
class TestGetOrRaise:
    def test_returns_instance_and_applies_filters(self):
        db = Mock()
        instance = object()
        db.query.return_value.filter_by.return_value.first.return_value = instance

        assert _fetch(db, user_id=3, is_active=True) is instance
        db.query.assert_called_once_with(Model)
        db.query.return_value.filter_by.assert_called_once_with(id=7, user_id=3, is_active=True)

    def test_missing_row_raises_not_found(self):
        db = Mock()
        db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(NotFound) as exc_info:
            _fetch(db)

        assert exc_info.value.message == "thing-7 not found"
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_db_error_raises_on_error_without_leaking_details(self):
        db = Mock()
        db_err = OperationalError("SELECT secret", None, Exception("password authentication failed"))
        db.query.return_value.filter_by.return_value.first.side_effect = db_err

        with pytest.raises(AppException) as exc_info:
            _fetch(db)

        assert exc_info.value.message == "database error while retrieving thing-7"
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.__cause__ is db_err
