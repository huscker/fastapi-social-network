from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from auth.api import user_router
from profile.api import profile_router
from feed.api import feed_router
from database.db import connect_db, disconnect_db

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup() -> None:
    if not connect_db():
        exit(0)


@app.on_event("shutdown")
async def shutdown() -> None:
    disconnect_db()


app.include_router(user_router)
app.include_router(profile_router)
app.include_router(feed_router)
