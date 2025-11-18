from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser
from app.taskapp.model import DocumentResponse, DocumentUpdate
from app.taskapp.dependencies import DependsDocumentService
from app.taskapp.exceptions import CollectionOperationException

router = APIRouter()

@router.put(
    '/{document_id}',
    response_model=DocumentResponse,
    summary='Update a document',
    description='Update an existing document by its ID',
    responses={
        200: {
            'description': 'Document updated successfully',
            'model': DocumentResponse
        },
        404: {'description': 'Document not found'},
        500: {'description': 'Internal server error'}
    }
)
def update_collection(document_id: int, payload: DocumentUpdate, current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentResponse:
    try:
        document_service.update_document(user_id=current_user.id, document_id=document_id, doc_col_data=payload)
        return DocumentResponse(message=f'DocumentCollection-{document_id} updated successfully')
    except CollectionOperationException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.message
        ) from err