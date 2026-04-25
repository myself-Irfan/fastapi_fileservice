from typing import Optional
from pydantic import BaseModel, Field, model_validator


class DocumentUpdateRequestModel(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Collection title")
    description: Optional[str] = Field(None, min_length=1, max_length=200, description="Collection description")

    @model_validator(mode='after')
    def ensure_one_exists(self):
        if self.title is None and self.description is None:
            raise ValueError('Provide at least one field to update')
        return self