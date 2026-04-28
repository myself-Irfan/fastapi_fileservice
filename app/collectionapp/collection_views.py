from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templates import templates

router = APIRouter(
    prefix='',
    tags=['Collection Views']
)


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


@router.get('/edit/{collection_id}', response_class=HTMLResponse)
def render_edit(request: Request, collection_id: int):
    """
    render edit collection page
    :param request:
    :return:
    """
    return templates.TemplateResponse('edit.html', {
        'request': request,
        'collection_id': collection_id
    })


@router.get('/{collection_id}', response_class=HTMLResponse)
def render_details(request: Request, collection_id: int):
    return templates.TemplateResponse('detail.html', {
        'request': request,
        'collection_id': collection_id
    })
