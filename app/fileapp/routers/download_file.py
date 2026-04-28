from fastapi import status, APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.auth.dependencies import CurrentUser
from app.fileapp.dependencies import DependsFileDownloadService
from app.fileapp.exceptions import FileOperationException
from app.logger import get_logger

router = APIRouter()

logger = get_logger(__name__)

@router.get(
    "/{file_id}/download",
    summary="download a file",
    description="download the actual file content",
    responses={
        200: {"description": "file downloaded successfully"},
        404: {"description": "file not found"},
        500: {"description": "internal server error"}
    }
)
async def download_file(file_id: int, current_user: CurrentUser, file_download_service: DependsFileDownloadService) -> FileResponse:
    try:
        file = file_download_service.get_file_path(
            user_id=current_user.id,
            file_id=file_id
        )
        return FileResponse(
            path=file.file_path,
            filename=file.title,
            media_type=file.mime_type
        )
    except FileOperationException as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
