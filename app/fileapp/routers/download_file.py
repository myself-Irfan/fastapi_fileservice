from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.auth.dependencies import CurrentUser
from app.fileapp.dependencies import DependsFileDownloadService

router = APIRouter()

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
    file = file_download_service.get_file_path(
        user_id=current_user.id,
        file_id=file_id
    )
    return FileResponse(
        path=file.file_path,
        filename=file.title,
        media_type=file.mime_type
    )
