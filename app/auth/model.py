from pydantic import BaseModel

from app.models import ApiResponse


class LoginTokenData(BaseModel):
    access_token: str
    refresh_token: str

class RefreshTokenData(BaseModel):
    access_token: str

class RefreshTokenResponse(ApiResponse):
    data: RefreshTokenData