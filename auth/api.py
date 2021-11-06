from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from . import schemas

templates = Jinja2Templates(directory="templates")

user_router = APIRouter()

@user_router.get('/register')
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@user_router.post('/register')
def register_new(user: schemas.UserIn):
    return {}

@user_router.get('/login')
def register(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


