from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser
from app.taskapp.dependencies import DependsDocumentService
from app.taskapp.model import DocumentResponse
from app.taskapp.exceptions import CollectionNotFoundException, CollectionOperationException
from app.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.delete(
    '/{document_id}',
    summary='Delete a DocumentCollection',
    description='Delete a DocumentCollection by its ID',
    responses={
        200: {'description': 'Document deleted successfully'},
        404: {'description': 'Document not found'},
        500: {'description': 'Internal server error'}
    }
)
def delete_collection(document_id: int, current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentResponse:
    try:
        document_service.delete_collection(current_user.id, document_id)
        return DocumentResponse(
            message=f'Document-{document_id} deleted successfully'
        )
    except CollectionOperationException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.message
        ) from err