from fastapi import APIRouter, Depends

from app.taskapp.routers.create_collection import router as create_col_router
from app.taskapp.routers.get_collection import router as collection_router
from app.taskapp.routers.delete_collection import router as delete_router
from app.taskapp.routers.update_collection import router as update_router
from app.taskapp.routers.get_all_collections import router as get_all_collections
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/api/tasks",
    tags=["Task APIs"],
    dependencies=[Depends(get_current_user)]
)
router.include_router(create_col_router)
router.include_router(collection_router)
router.include_router(delete_router)
router.include_router(update_router)
router.include_router(get_all_collections)