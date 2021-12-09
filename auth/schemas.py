from pydantic import BaseModel


class User(BaseModel):
    login: str
    password: str


class UserNew(User):
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str
