from datetime import datetime, timedelta
from typing import Union

from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.user.service import get_user_by_email
from src.dependencies import verify_password

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



class Token(BaseModel):
    access_token: str
    token_type: str




def authenticate_user(db:Session, email: str, password: str):
    user = get_user_by_email(db, email)
    print(user)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

