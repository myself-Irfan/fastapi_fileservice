from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser
from app.collectionapp.dependencies import DependsDocumentService
from app.collectionapp.models.read_document_model import DocumentListResponseModel
from app.collectionapp.exceptions import CollectionOperationException

router = APIRouter()


@router.get(
    "/",
    response_model=DocumentListResponseModel,
    summary="Get all documents",
    description="Retrieve all documents from the database",
    responses={
        200: {
            "description": "Documents retrieved successfully",
            "model": DocumentListResponseModel
        },
        500: {"description": "Internal server error"}
    }
)
def get_all_collections(current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentListResponseModel:
    try:
        collections = document_service.fetch_documents(user_id=current_user.id)
        message = "Collections retrieved successfully" if collections else f"No collection found for {current_user.name}"

        return DocumentListResponseModel(
            message=message,
            data=collections or []
        )
    except CollectionOperationException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.message
        ) from err