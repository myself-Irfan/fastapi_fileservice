from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser
from app.taskapp.dependencies import DependsDocumentService
from app.taskapp.model import DocumentListResponse
from app.taskapp.exceptions import CollectionOperationException

router = APIRouter()


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="Get all documents",
    description="Retrieve all documents from the database",
    responses={
        200: {
            "description": "Documents retrieved successfully",
            "model": DocumentListResponse
        },
        500: {"description": "Internal server error"}
    }
)
def get_all_collections(current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentListResponse:
    try:
        collections = document_service.fetch_documents(user_id=current_user.id)
        message = "Collections retrieved successfully" if collections else f"No collection found for {current_user.name}"

        return DocumentListResponse(
            message=message,
            data=collections or []
        )
    except CollectionOperationException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=err.message
        ) from err