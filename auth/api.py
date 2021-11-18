from fastapi import APIRouter, Depends, Form, status, HTTPException
from fastapi.requests import Request
from fastapi.responses import RedirectResponse,JSONResponse
from . import schemas
from .login import login_for_access_token,register_user
from database import db

user_router = APIRouter()

@user_router.post('/registration',response_model=schemas.UserNew)
def register_new(user : schemas.UserNew):
    if register_user(user):
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or login is not unique",
            headers={"WWW-Authenticate": "Bearer"},
        )

@user_router.post('/login',response_model=schemas.Token)
def authenticate(login : str = Form(...),password : str = Form(...)):
    return login_for_access_token(login,password)



