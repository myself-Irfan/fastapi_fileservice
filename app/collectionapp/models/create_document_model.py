from app.collectionapp.models.base_document_model import DocumentBase
from app.models import ApiResponse


class DocumentCreateRequestModel(DocumentBase):
    pass

class DocumentCreateResponseModel(ApiResponse):
    id: int