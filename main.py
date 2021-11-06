from fastapi import FastAPI,Path,Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from auth.api import user_router

class Item(BaseModel):
    name: str
    surname: Optional[str] = None

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get('/',response_class=HTMLResponse)
def index(request : Request):
    return templates.TemplateResponse('index.html', {"request":request})

@app.get('/feed/{feed_id}')
def get_feed_by_id(feed_id:int = Path(None,description="greater than zero",gt=0)):
    return {"asd":feed_id}

@app.post('/test')
def test(item : Item):
    return item

app.include_router(user_router)