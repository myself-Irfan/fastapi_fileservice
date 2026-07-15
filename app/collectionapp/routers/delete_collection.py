from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser
from app.collectionapp.dependencies import DependsDocumentService

router = APIRouter()


@router.delete(
    '/{document_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete a DocumentCollection',
    description='Delete a DocumentCollection by its ID',
    responses={
        204: {'description': 'Document deleted successfully'},
        404: {'description': 'Document not found'},
        500: {'description': 'Internal server error'}
    }
)
def delete_collection(document_id: int, current_user: CurrentUser, document_service: DependsDocumentService) -> None:
    document_service.delete_collection(current_user.id, document_id)