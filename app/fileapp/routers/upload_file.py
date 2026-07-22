from fastapi import status, UploadFile, File, Form, APIRouter, HTTPException, Response
from typing import Optional

from app.auth.dependencies import CurrentUser
from app.fileapp.model import FileReadResponse
from app.fileapp.dependencies import DependsFileUploadService
from app.logger import get_logger

router = APIRouter()

logger = get_logger(__name__)

@router.post(
    "/upload",
    response_model=FileReadResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    summary="upload a file",
    description="upload a file. optionally link with a document.",
    responses={
        201: {
            "description": "file uploaded successfully",
            "model": FileReadResponse
        },
        400: {"description": "invalid file or parameters"},
        404: {"description": "document not found"},
        500: {"description": "internal server error"}
    }
)
def upload_file(
    response: Response,
    current_user: CurrentUser,
    file_upload_service: DependsFileUploadService,
    file: UploadFile = File(...),
    document_id: Optional[int] = Form(None, description="document id to link file with"),
) -> FileReadResponse:
    logger.info(
        "file upload request received",
        filename=file.filename,
        user_id=current_user.id,
        document_id=document_id
    )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no filename provided"
        )

    uploaded_file = file_upload_service.upload_file(
        file=file,
        user_id=current_user.id,
        document_id=document_id
    )
    response.headers["Location"] = f"/api/files/{uploaded_file.id}"
    return FileReadResponse(message="file upload successful", data=uploaded_file)
