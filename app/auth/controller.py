from fastapi import APIRouter, Header

from app.auth.exceptions import AuthenticationError
from app.auth.service import AuthenticationService
from app.auth.model import RefreshTokenResponse, RefreshTokenData
from app.database.core import DbSession

router = APIRouter(
    prefix='/api/auth',
    tags=['Authentication APIs']
)


@router.post(
    "/refresh-token",
    response_model=RefreshTokenResponse,
    summary='Refresh access token',
    description='Generate a new access token using a valid refresh token',
    responses={
        200: {
            'description': 'Access token refreshed successfully',
            'model': RefreshTokenResponse
        },
        401: {'description': 'Invalid or expired refresh token'},
        500: {'description': 'Internal server error'}
    }
)
def refresh_user_access_token(db: DbSession, authorization: str = Header(...)) -> RefreshTokenResponse:
    """
    Refresh user access token using a valid refresh token
    """

    if not authorization.startswith("Bearer "):
        raise AuthenticationError('Invalid Authorization header format')

    refresh_token = authorization.removeprefix("Bearer").strip()

    new_access_token = AuthenticationService.refresh_access_token(refresh_token, db)

    return RefreshTokenResponse(
        message='Access token refreshed successfully',
        data=RefreshTokenData(
            access_token=new_access_token
        )
    )