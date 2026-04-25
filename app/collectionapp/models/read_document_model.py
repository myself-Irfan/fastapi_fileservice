from datetime import datetime
from typing import Optional, List
from pydantic import Field, ConfigDict

from app.collectionapp.models.base_document_model import DocumentBase, ApiResponse


class DocumentReadModel(DocumentBase):
    id: int = Field(..., gt=0, description="Collection ID")
    created_at: datetime = Field(..., description="Collection creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Collection last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponseModel(ApiResponse):
    data: Optional[List[DocumentReadModel]] = None


class DocumentResponseModel(ApiResponse):
    data: Optional[DocumentReadModel] = None