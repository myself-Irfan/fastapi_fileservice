from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser
from app.taskapp.dependencies import DependsDocumentService
from app.taskapp.model import DocumentResponse
from app.logger import get_logger
from app.taskapp.exceptions import CollectionOperationException

router = APIRouter()
logger = get_logger()


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary='Get a collection by ID',
    description='Retrieve a specific collection by its ID',
    responses={
        200: {
            'description': 'Collection retrieved successfully',
            'model': DocumentResponse
        },
        404: {'description': 'Collection not found'},
        500: {'description': 'Internal server error'}
    }
)
def get_collection(document_id: int, current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentResponse:
    try:
        task = document_service.fetch_document_by_id(document_id=document_id, user_id=current_user.id)
        return DocumentResponse(
            message='Collection retrieved successfully',
            data=task
        )
    except CollectionOperationException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.message
        ) from err