from pydantic import BaseModel, Field, ConfigDict


class ApiResponse(BaseModel):
    """API response wrapper."""
    message: str = Field(..., description="Response message")

    model_config = ConfigDict(from_attributes=True)
