from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templates import templates

router = APIRouter(
    prefix='/files',
    tags=['File Views']
)


@router.get('/', response_class=HTMLResponse)
def render_files(request: Request):
    return templates.TemplateResponse('files.html', {'request': request})