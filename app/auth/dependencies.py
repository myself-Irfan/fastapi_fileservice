from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated

from app.database.core import DbSession
from app.userapp.entities import DocumentUser
from app.auth.enums import TokenType
from app.auth.exceptions import AuthenticationError
from app.exceptions import AppException
from app.auth.service import AuthenticationService
from app.logger import get_logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login')
logger = get_logger(__name__)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> DocumentUser:
    """
    Get current user from JWT token
    :param token:
    :param db:
    :return:
    """

    try:
        user_id = AuthenticationService.get_user_from_token(
            token,
            token_type=TokenType.ACCESS
        )

        if not user_id:
            logger.warning('Invalid or expired token')
            raise AuthenticationError('Invalid/expired token')

        user = db.get(DocumentUser, user_id)
        if not user:
            logger.warning(f'User-{user_id} not found')
            raise AuthenticationError(f'User-{user_id} not found')
        return user
    except SQLAlchemyError as err:
        logger.error('user retrieval failed', error_type='database error', error=str(err), exc_info=True)
        raise AppException('Database error', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from err


CurrentUser = Annotated[DocumentUser, Depends(get_current_user)]