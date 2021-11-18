from fastapi import FastAPI,Path,Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from auth.api import user_router
from profile.api import profile_router
from feed.api import feed_router
from database.db import connect_db,disconnect_db

class Item(BaseModel):
    name: str
    surname: Optional[str] = None

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/')
def index(request : Request):
    return ""

@app.on_event("startup")
async def startup() -> None:
    if not connect_db():
        pass # shutdown

@app.on_event("shutdown")
async def shutdown() -> None:
    disconnect_db()

app.include_router(user_router)
app.include_router(profile_router)
app.include_router(feed_router)