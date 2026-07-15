from fastapi import APIRouter, status, Request

from app.rate_limiter import limiter
from app.config import settings
from app.userapp.dependencies import DependsUserService
from app.userapp.model import UserRegister, ApiResponse

router = APIRouter()


@router.post(
    '/register',
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Register an user',
    description='Take name, email and password to register an user',
    responses={
        201: {
            "description": 'User created successfully',
            'model': ApiResponse
        },
        400: {'description': 'Email already in use'},
        500: {'description': 'Internal server error'}
    }
)
@limiter.limit(f"{settings.register_limit_per_hour}/hour")
def register_user(request: Request, payload: UserRegister, user_service: DependsUserService) -> ApiResponse:
    user = user_service.create_registered_user(payload)
    return ApiResponse(
        message=f'User-{user.id} created successfully',
    )
