from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import CurrentUser
from app.taskapp.dependencies import DependsDocumentService
from app.taskapp.models.create_document_model import DocumentCreateRequestModel, DocumentCreateResponseModel
from app.taskapp.exceptions import CollectionOperationException

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
def create_task(payload: DocumentCreateRequestModel, current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentCreateResponseModel:
    try:
        task_id = document_service.create_document(current_user.id, payload)
        return DocumentCreateResponseModel(
            message='created successfully',
            id=task_id
        )
    except CollectionOperationException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.message
        ) from err