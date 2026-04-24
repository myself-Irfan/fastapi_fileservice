from fastapi import FastAPI

from app.auth.controller import router as auth_api_router
from app.taskapp.routers import router as collection_api_router
from app.userapp.routers import router as user_api_router
from app.userapp.view import router as user_view_router
from app.taskapp.task_views import router as task_view_router
from app.fileapp.routers.base_controller import router as file_api_router


def register_routers(app: FastAPI):
    app.include_router(auth_api_router)
    app.include_router(user_api_router)
    app.include_router(user_view_router)
    app.include_router(collection_api_router)
    app.include_router(task_view_router)
    app.include_router(file_api_router)