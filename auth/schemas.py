from pydantic import EmailStr, BaseModel


class User(BaseModel):
    username: str
    login: str


class UserIn(User):
    token: str


class UserUpdate(User):
    pass


class UserOut(BaseModel):
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str
