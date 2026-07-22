from fastapi import APIRouter, Response, status

from app.auth.dependencies import CurrentUser
from app.collectionapp.dependencies import DependsDocumentService
from app.collectionapp.models.create_document_model import DocumentCreateRequestModel, DocumentCreateResponseModel

router = APIRouter()

@router.post(
    "/",
    response_model=DocumentCreateResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new Document object',
    description='Add a Document object to DocumentCollection table database',
    responses={
        201: {
            'description': 'Document created',
            'model': DocumentCreateResponseModel
        },
        500: {'description': 'Internal server error'}
    }
)
def create_task(response: Response, payload: DocumentCreateRequestModel, current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentCreateResponseModel:
    collection_id = document_service.create_document(current_user.id, payload)
    response.headers["Location"] = f"/api/collection/{collection_id}"
    return DocumentCreateResponseModel(
        message='created successfully',
        id=collection_id
    )