from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser
from app.taskapp.models.read_document_model import DocumentResponseModel
from app.taskapp.models.update_document_model import DocumentUpdateRequestModel
from app.taskapp.dependencies import DependsDocumentService
from app.taskapp.exceptions import CollectionOperationException

router = APIRouter()

@router.put(
    '/{document_id}',
    response_model=DocumentResponseModel,
    summary='Update a document',
    description='Update an existing document by its ID',
    responses={
        200: {
            'description': 'Document updated successfully',
            'model': DocumentResponseModel
        },
        404: {'description': 'Document not found'},
        500: {'description': 'Internal server error'}
    }
)
def update_collection(document_id: int, payload: DocumentUpdateRequestModel, current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentResponseModel:
    try:
        document_service.update_document(user_id=current_user.id, document_id=document_id, doc_col_data=payload)
        return DocumentResponseModel(message=f'DocumentCollection-{document_id} updated successfully')
    except CollectionOperationException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.message
        ) from err