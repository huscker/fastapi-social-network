from typing import Optional

from fastapi import APIRouter, status, Path, HTTPException, File, UploadFile, Header
from fastapi.responses import JSONResponse

from auth.login import get_current_user
from database.db import DB
from feed.feed import update_post_data

feed_router = APIRouter()


@feed_router.get('/feed')
async def get_feed():
    '''
    Get all posts
    '''
    posts = await DB.get_all_posts()
    posts = update_post_data(posts)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'posts': posts
    })


@feed_router.get('/feed/{n_posts}')
async def get_n_posts(n_posts: int = Path(..., gt=0, description='Number of random posts to be returned')):
    '''
    Get user defined number of posts
    '''
    posts = await DB.get_random_n_posts(n_posts)
    posts = update_post_data(posts)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'posts': posts
    })


@feed_router.get('/feed/page/{page}')
async def gen_posts_by_page(page: int = Path(..., gt=0, description='Page number')):
    '''
    Get posts on page
    '''
    posts = await DB.get_all_posts_with_paging(page)
    if posts:
        posts = update_post_data(posts)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'posts': posts
    })


@feed_router.get('/feed/post/{feed_id}')
async def get_post(feed_id: int = Path(..., gt=0, description='Post id')):
    '''
    Get post by id
    '''
    post = await DB.get_post(feed_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid feed id"
        )
    post = update_post_data([post])[0]
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'post': post,
    })


@feed_router.get('/feed/user/{user_id}')
async def get_posts_of_user(user_id: int = Path(..., gt=0, description='User id')):
    '''
    Get posts of user by id
    '''
    posts = await DB.get_posts_of_user(user_id)
    posts = update_post_data(posts)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'posts': posts
    })


@feed_router.post('/feed/like/{feed_id}')
async def like_post(feed_id: int = Path(..., gt=0, description='Post id'),
                    access_token: Optional[str] = Header(None, description='JWT auth token')):
    '''
    Like post if authorized
    '''
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_current_user(access_token)
    if not await DB.like_post(user[0], feed_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked or invalid id"
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'detail': "Executed",
    })


@feed_router.post('/feed/unlike/{feed_id}')
async def unlike_post(feed_id: int = Path(..., gt=0, description='Post id'),
                      access_token: Optional[str] = Header(None, description='JWT auth token')):
    '''
    Remove like if authorized
    '''
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_current_user(access_token)
    if not await DB.unlike_post(user[0], feed_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already unliked or invalid id"
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'detail': "Executed",
    })


@feed_router.delete('/feed/post/{feed_id}')
async def delete_post(
        feed_id: int = Path(..., gt=0, description='Post id'),
        access_token: Optional[str] = Header(None, description='JWT auth token')):
    '''
    Delete post and data, associated with it if authorized
    '''
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_current_user(access_token)
    post = await DB.get_post(feed_id)
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
    if not await DB.delete_post(feed_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown error"
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'detail': "Executed",
    })


@feed_router.post('/feed')
async def add_new_post(
        title: str,
        description: str,
        photo_file: UploadFile = File(..., description='Upload file'),
        access_token: Optional[str] = Header(None, description='JWT auth token')):
    '''
    Add new post if authorized
    '''
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_current_user(access_token)
    id = await DB.add_new_post(title, description, photo_file, user[0])
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
