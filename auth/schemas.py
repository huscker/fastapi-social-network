from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    login: str


class UserIn(User):
    token: str


class UserNew(User):
    password:str


class Token(BaseModel):
    access_token: str
    token_type: str

