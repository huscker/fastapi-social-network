# TODO: remove JWT from Cookies
# TODO: remove actions as queries
# TODO: change error HTTP_401 to other codes
from fastapi import APIRouter, Depends, Form, status, Path, HTTPException, Cookie,File,UploadFile, Header
from fastapi.requests import Request
from fastapi.responses import RedirectResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from database import db
from auth import schemas
from feed import feed
from auth.login import get_current_user,get_password_hash
from database import db

profile_router = APIRouter()


@profile_router.get('/id{user_id}')
def get_profile_of(request: Request, user_id: int = Path(..., gt=0), action: Optional[str] = None,
                   access_token: Optional[str] = Cookie(None)):
    user = db.get_user_by_id_db(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect id"
        )
    posts = db.get_posts_of_user(user_id)
    posts = feed.update_post_data(posts)
    return posts


@profile_router.get('/profile')
def get_my_profile(access_token : Optional[str] = Header(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_current_user(access_token)
    posts = db.get_post(user[0])
    if posts is None:
        posts = list()
    return JSONResponse(status_code=status.HTTP_200_OK,content={
        'id':user[0],
        'username':user[3],
        'login':user[1],
        'posts':posts
    })

@profile_router.put('/profile')
def change_profile(
        access_token: Optional[str] = Header(None),
        username: Optional[str] = Header(None),
        password: Optional[str] = Header(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = list(get_current_user(access_token))
    print(password,username)
    if password is not None:
        user[2] = password
    if username is not None:
        user[3] = username
    if not db.update_user_db(get_password_hash(user[2]),user[3],user[0]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is not unique"
        )
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={
        'name':user[3]
    })


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

@profile_router.get('/profile/delete/{feed_id}')
def delete_post(request: Request,feed_id: int = Path(..., gt=0) ,access_token: Optional[str] = Cookie(None)):
    if access_token:
        user = get_current_user(access_token)  # add exception handler
        # update db
        if not db.delete_post(feed_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No such post",
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
