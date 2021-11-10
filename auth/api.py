from fastapi import APIRouter, Depends, Form, status, HTTPException
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from . import schemas
from .login import login_for_access_token,register_user
from database import db

templates = Jinja2Templates(directory="templates")

user_router = APIRouter()

@user_router.get('/register')
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@user_router.post('/register')
def register_new(username:str = Form(...),login:str=Form(...),password:str=Form(...)):
    if register_user(username,login,password):
        return RedirectResponse('/',status_code=status.HTTP_302_FOUND)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or login is not unique",
            headers={"WWW-Authenticate": "Bearer"},
        )

@user_router.get('/login')
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@user_router.post('/login',response_model=schemas.Token)
def authenticate(login : str = Form(...),password : str = Form(...)):
    resp = RedirectResponse("/profile",status_code=status.HTTP_302_FOUND)
    resp.set_cookie("access_token",
                    value=f"{login_for_access_token(login,password)['access_token']}",
                    max_age=10
                    )
    return resp



