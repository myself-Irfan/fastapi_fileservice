from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from app.auth.dependencies import CurrentUser
from app.fileapp.model import FileReadResponse, FileListResponse
from app.logger import get_logger
from app.fileapp.services.base_service import FileService
from app.fileapp.routers.upload_file import router as upload_router
from app.fileapp.routers.download_file import router as download_router
from app.fileapp.dependencies import get_file_service

router = APIRouter(
    prefix="/api/files",
    tags=["Collection File APIs"],
)
router.include_router(upload_router)
router.include_router(download_router)

logger = get_logger(__name__)


@router.get(
    "/",
    response_model=FileListResponse,
    summary="get all files",
    description="retrieve all files for current user. optionally filter by document id",
    responses={
        200: {
            "description": "files retrieval successful",
            "model": FileListResponse
        },
        500: {"description": "internal server error"}
    }
)
def get_all_files(
        current_user: CurrentUser,
        document_id: Optional[int] = Query(None, description="filter by document id"),
        file_service: FileService = Depends(get_file_service)
) -> FileListResponse:

    try:
        files = file_service.fetch_files(
            user_id=current_user.id,
            document_id=document_id
        )
        message = "files retrieval success" if files else "no files to retrieve"

        return FileListResponse(
            message=message,
            data=files or []
        )
    except SQLAlchemyError as sql_err:
        logger.error("files retrieval failed", error_type="database error", error=sql_err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="files retrieval failed"
        )
    except Exception as err:
        logger.error("files retrieval failed", error_type="unexpected error", error=err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="files retrieval failed"
        )


@router.get(
    "/{file_id}",
    response_model=FileReadResponse,
    summary="retrieve file by id",
    description="retrieve a file by its ID",
    responses={
        200: {
            "description": "file retrieval success",
            "model": FileReadResponse
        },
        404: {"description": "file not found"},
        500: {"description": "internal server error"}
    }
)
def get_file(
        file_id: int,
        current_user: CurrentUser,
        file_service: FileService = Depends(get_file_service)
) -> FileReadResponse:

    try:
        file = file_service.fetch_file_by_id(
            user_id=current_user.id,
            file_id=file_id
        )

        return FileReadResponse(
            message="file retrieval successful",
            data=file
        )
    except HTTPException:
        raise
    except SQLAlchemyError as sql_err:
        logger.error("file retrieval failed", error_type="database error", file_id=file_id, error=sql_err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="file retrieval failed"
        ) from sql_err
    except Exception as err:
        logger.error("file retrieval failed", error_type="unexpected error", file_id=file_id, error=err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="file retrieval failed"
        ) from err


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="delete a file",
    description="soft delete a file",
    responses={
        204: {"description": "file deleted successfully"},
        404: {"description": "file not found"},
        500: {"description": "internal server error"}
    }
)
def delete_file(
        file_id: int,
        current_user: CurrentUser,
        file_service: FileService = Depends(get_file_service)
) -> None:

    try:
        file_service.delete_file(
            user_id=current_user.id,
            file_id=file_id
        )
    except HTTPException:
        raise
    except SQLAlchemyError as sql_err:
        logger.error("file deletion failed", error_type="database error", file_id=file_id, error=sql_err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"file-{file_id} deletion failed"
        )
    except Exception as err:
        logger.error("file deletion failed", error_type="unexpected error", file_id=file_id, error=err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"file-{file_id} deletion failed"
        )