from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter(
    prefix='',
    tags=['Collection Views']
)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory='templates')


@router.get('/', response_class=HTMLResponse)
def render_index(request: Request):
    """
    render the main collection list page
    :param request:
    :return:
    """
    return templates.TemplateResponse('index.html', {'request': request})


@router.get('/create', response_class=HTMLResponse)
def render_create(request: Request):
    """
    render create collection page
    :param request:
    :return:
    """
    return templates.TemplateResponse('create.html', {'request': request})


@router.get('/edit/{task_id}', response_class=HTMLResponse)
def render_edit(request: Request, task_id: int):
    """
    render edit collection page
    :param request:
    :return:
    """
    return templates.TemplateResponse('edit.html', {
        'request': request,
        'task_id': task_id
    })


@router.get('/{task_id}', response_class=HTMLResponse)
def render_details(request: Request, task_id: int):
    return templates.TemplateResponse('detail.html', {
        'request': request,
        'task_id': task_id
    })
