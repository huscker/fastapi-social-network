from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from configs.config import Config
from database.db import DB
from . import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    '''
    Return if password matches hashed version
    :param plain_password:
    :param hashed_password:
    :return: True or False
    '''
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    '''
    Get hashed version of password
    :param password:
    :return: str()
    '''
    return pwd_context.hash(password)


async def register_user(user: schemas.UserNew):
    '''
    Add new user to db
    :param user:
    :return: True or False
    '''
    return await DB.add_new_user_db(user.login, get_password_hash(user.password), user.username)


async def authenticate_user(login: str, password: str):
    '''
    Get user if authorized
    :param login:
    :param password:
    :return: list() or False
    '''
    user = await DB.get_user_by_login_db(login)
    if not user:
        return False
    if not verify_password(password, user[2]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    '''
    Generate auth token
    :param data:
    :param expires_delta: Optional
    :return: str()
    '''
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    '''
    Get user by auth token
    :param token:
    :return: list() or credentials_exception
    '''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await DB.get_user_by_login_db(username)
    if user is None:
        raise credentials_exception
    return user


async def login_for_access_token(login: str, password: str):
    '''
    Login user and return token
    :param login:
    :param password:
    :return: dict()
    '''
    user = await authenticate_user(login, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user[1]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
