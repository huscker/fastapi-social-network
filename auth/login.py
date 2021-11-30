from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta
from . import schemas
from database.db import add_new_user_db, get_user_by_login_db

SECRET_KEY = '8b8a819d4276f27ffa673b45d8fb85bee7272c91549cce9b120ee88a44746d9e'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 5

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def register_user(user: schemas.UserNew):
    return add_new_user_db(user.login, get_password_hash(user.password), user.username)


def authenticate_user(login: str, password: str):
    user = get_user_by_login_db(login)
    if not user:
        return False
    if not verify_password(password, user[2]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_login_db(username)
    if user is None:
        raise credentials_exception
    return user


def login_for_access_token(login: str, password: str):
    user = authenticate_user(login, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user[1]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
