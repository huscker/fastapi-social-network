import sys

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from auth.api import user_router
from database.db import DB
from feed.api import feed_router
from profile.api import profile_router

app = FastAPI(
    title='Social Network',
    version='1.0.0'
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup() -> None:
    '''
    Connect to db
    :return:
    '''
    if not await DB.connect_db():
        sys.exit(0)


@app.on_event("shutdown")
async def shutdown() -> None:
    '''
    Disconnect from db
    :return:
    '''
    await DB.disconnect_db()


app.include_router(user_router)
app.include_router(profile_router)
app.include_router(feed_router)
