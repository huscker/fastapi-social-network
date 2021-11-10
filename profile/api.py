# TODO: remove JWT from Cookies

from fastapi import APIRouter, Depends, Form, status, Path, HTTPException, Cookie,File,UploadFile
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from database import db
from auth import schemas
from auth.login import get_current_user,get_password_hash
from database import db

templates = Jinja2Templates(directory="templates")

profile_router = APIRouter()


@profile_router.get('/id{user_id}')
def get_profile_of(request: Request, user_id: int = Path(..., gt=0), action: Optional[str] = None,
                   access_token: Optional[str] = Cookie(None)):
    user = db.get_user_by_id_db(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    authorized = False
    if access_token:
        user2 = get_current_user(access_token)  # add exception handler
        if user2[0] == user[0]:
            authorized = True
    resp = templates.TemplateResponse("profile.html", {
        "request": request,
        'username': user[3],
        'authorized': authorized,
        'edit': action == 'edit',
        'add': action == 'add'
    })
    if access_token:
        resp.set_cookie("access_token",
                        value=f"{access_token}",
                        max_age=10
                        )
    return resp


@profile_router.get('/profile')
def get_my_profile(action: Optional[str] = None, access_token: Optional[str] = Cookie(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_current_user(access_token) #
    if action:
        resp = RedirectResponse(f'/id{user[0]}?action={action}', status_code=status.HTTP_302_FOUND)
    else:
        resp = RedirectResponse(f'/id{user[0]}', status_code=status.HTTP_302_FOUND)
    resp.set_cookie("access_token",
                    value=f"{access_token}",
                    max_age=10
                    )
    return resp


@profile_router.post('/profile/edit')
def upload_or_edit(request: Request,username : str = Form(...),password : str = Form(...), access_token: Optional[str] = Cookie(None)):
    if access_token:
        user = get_current_user(access_token)  # add exception handler
        if not db.update_user_db(get_password_hash(password),username,user[0]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username is not unique",
                headers={"WWW-Authenticate": "Bearer"},
            )
        resp = RedirectResponse('/profile', status_code=status.HTTP_302_FOUND)
        resp.set_cookie('access_token',
                        value=f'{access_token}',
                        max_age=10
                        )
        return resp
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )

@profile_router.post('/profile/add')
def upload_or_edit(request: Request,title : str = Form(...),description : str = Form(...),file_photo : UploadFile = File(...), access_token: Optional[str] = Cookie(None)):
    if access_token:
        user = get_current_user(access_token)  # add exception handler
        # update db
        db.add_new_post(title,description,file_photo,user[0]) # add exception handler
        resp = RedirectResponse('/profile', status_code=status.HTTP_302_FOUND)
        resp.set_cookie('access_token',
                        value=f'{access_token}',
                        max_age=10
                        )
        return resp
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
