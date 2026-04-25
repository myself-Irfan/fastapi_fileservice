from fastapi import APIRouter

from app.collectionapp.routers.create_collection import router as create_col_router
from app.collectionapp.routers.get_collection import router as collection_router
from app.collectionapp.routers.delete_collection import router as delete_router
from app.collectionapp.routers.update_collection import router as update_router
from app.collectionapp.routers.get_all_collections import router as get_all_collections

router = APIRouter(
    prefix="/api/collection",
    tags=["Collection APIs"],
)
router.include_router(create_col_router)
router.include_router(collection_router)
router.include_router(delete_router)
router.include_router(update_router)
router.include_router(get_all_collections)