from fastapi import APIRouter, status, Path, HTTPException, File, UploadFile, Header
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from auth.login import get_current_user
from database import db
from feed.feed import update_post_data

templates = Jinja2Templates(directory="templates")

feed_router = APIRouter()


@feed_router.get('/feed')
def get_feed():
    posts = db.get_all_posts()
    posts = update_post_data(posts)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'posts': posts
    })


@feed_router.get('/feed/{n_posts}')
def get_n_posts(n_posts: int = Path(..., gt=0)):
    posts = db.get_random_n_posts(n_posts)
    posts = update_post_data(posts)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'posts': posts
    })


@feed_router.get('/feed/page/{page}')
def gen_posts_by_page(page: int = Path(..., gt=0)):
    posts = db.get_all_posts_with_paging(page)
    print(posts)
    if posts:
        posts = update_post_data(posts)
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            'posts': posts
        })
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            'posts': []
        })


@feed_router.get('/feed/post/{feed_id}')
def get_post(feed_id: int = Path(..., gt=0)):
    post = db.get_post(feed_id)
    if post:
        post = update_post_data([post])[0]
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            'post': post,
        })
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid feed id"
        )


@feed_router.get('/feed/user/{user_id}')
def get_posts_of_user(user_id: int = Path(..., gt=0)):
    posts = db.get_posts_of_user(user_id)
    posts = update_post_data(posts)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'posts': posts
    })


@feed_router.post('/feed/like/{feed_id}')
def like_post(feed_id: int = Path(..., gt=0), access_token: Optional[str] = Header(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_current_user(access_token)
    if not db.like_post(user[0], feed_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked or invalid id"
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'detail': "Executed",
    })


@feed_router.post('/feed/unlike/{feed_id}')
def unlike_post(feed_id: int = Path(..., gt=0), access_token: Optional[str] = Header(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_current_user(access_token)
    if not db.unlike_post(user[0], feed_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown error"
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'detail': "Executed",
    })


@feed_router.delete('/feed/post/{feed_id}')
def delete_post(
        feed_id: int = Path(..., gt=0),
        access_token: Optional[str] = Header(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_current_user(access_token)
    post = db.get_post(feed_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid feed id"
        )
    if post[2] != user[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post doesnt belong to user"
        )
    if not db.delete_post(feed_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown error"
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'detail': "Executed",
    })


@feed_router.post('/feed')
def add_new_post(
        title: str,
        description: str,
        photo_file: UploadFile = File(...),
        access_token: Optional[str] = Header(None)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_current_user(access_token)
    id = db.add_new_post(title, description, photo_file, user[0])
    if not id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post title is not unique"
        )
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={
        'id': id[0],
        'title': title,
        'description': description
    })
