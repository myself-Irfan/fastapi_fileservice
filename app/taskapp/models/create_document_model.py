from app.taskapp.models.base_document_model import DocumentBase, ApiResponse


class DocumentCreateRequestModel(DocumentBase):
    pass

class DocumentCreateResponseModel(ApiResponse):
    id: int