from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templates import templates

router = APIRouter(
    prefix='',
    tags=['User Views']
)


@router.get(
    '/register',
    response_class=HTMLResponse,
    summary='Render user registration page',
    description='Render the user registration page where new users can sign up'
)
def render_register(request: Request):
    """
    render register user page
    :param request:
    :return:
    """
    return templates.TemplateResponse('register.html', {'request': request})


@router.get('/login', response_class=HTMLResponse)
def login_user(request: Request):
    """
    render user login page
    :param request:
    :return:
    """
    return templates.TemplateResponse('login.html', {'request': request})