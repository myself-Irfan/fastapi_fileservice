from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Collection title")
    description: Optional[str] = Field(None, max_length=200, description="Collection description")

    @field_validator('title', mode='before')
    @classmethod
    def strip_title(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError('title cannot be blank')
        return v

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Collection title")
    description: Optional[str] = Field(None, min_length=1, max_length=200, description="Collection description")

    @model_validator(mode='after')
    def ensure_one_exists(self):
        if self.title is None and self.description is None:
            raise ValueError('Provide at least one field to update')
        return self

class DocumentRead(DocumentBase):
    id: int = Field(..., gt=0, description="Collection ID")
    created_at: datetime = Field(..., description="Collection creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Collection last update timestamp")

    model_config = ConfigDict(from_attributes=True)

class ApiResponse(BaseModel):
    """API response wrapper."""
    message: str = Field(..., description="Response message")

    model_config = ConfigDict(from_attributes=True)

# Specific response schemas for better type safety
class DocumentListResponse(ApiResponse):
    """Response schema for taskapp list endpoints."""
    data: Optional[List[DocumentRead]] = None

class DocumentResponse(ApiResponse):
    """Response schema for single taskapp endpoints."""
    data: Optional[DocumentRead] = None