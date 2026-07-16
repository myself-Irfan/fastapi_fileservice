from typing import Optional
from pydantic import BaseModel, Field, field_validator


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