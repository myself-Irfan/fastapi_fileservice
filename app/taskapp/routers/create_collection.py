from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import CurrentUser
from app.taskapp.dependencies import DependsDocumentService
from app.taskapp.model import ApiResponse, DocumentCreate, DocumentResponse
from app.taskapp.exceptions import CollectionOperationException

router = APIRouter()

@router.post(
    "/",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new Document object',
    description='Add a Document object to DocumentCollection table database',
    responses={
        201: {
            'description': 'Document created',
            'model': ApiResponse
        },
        500: {'description': 'Internal server error'}
    }
)
def create_task(payload: DocumentCreate, current_user: CurrentUser, document_service: DependsDocumentService) -> ApiResponse:
    try:
        task_id = document_service.create_document(current_user.id, payload)
        return DocumentResponse(
            message=f'DocumentCollection-{task_id} created successfully'
        )
    except CollectionOperationException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.message
        ) from err