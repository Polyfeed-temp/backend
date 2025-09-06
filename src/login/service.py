from datetime import datetime, timedelta
from typing import Union
from fastapi import Depends, HTTPException, status, Header, Request
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.user.service import get_user_by_email
from src.dependencies import verify_password, oauth2_scheme
from src.user.schemas import UserPydantic
from src.database import get_db

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

# Initialize Firebase Admin SDK only if certificate exists
firebase_initialized = False
firebase_cert_path = "src/northern-audio-405809-firebase-adminsdk-myq2f-41e88bfe44.json"

if os.path.exists(firebase_cert_path):
    cred = credentials.Certificate(firebase_cert_path)
    app = firebase_admin.initialize_app(cred)
    firebase_initialized = True
else:
    # Try to initialize with environment variables or default credentials
    try:
        # For production, you might use Application Default Credentials
        app = firebase_admin.initialize_app()
        firebase_initialized = True
    except Exception:
        # Firebase not configured - will handle in verify_firebase_token
        pass


def verify_firebase_token(id_token: str):
    """
    Verify Firebase ID token and return user email
    """
    if not firebase_initialized:
        print("Firebase not initialized - token verification unavailable")
        return None
        
    try:
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token.get('email')
        return email
    except Exception as e:
        print(f"Firebase token verification failed: {e}")
        return None



class UserResponse(BaseModel):
    user: UserPydantic
    access_token: str


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    
    # Check if user uses local authentication (has password)
    # Firebase users authenticate via Firebase tokens, not passwords
    if hasattr(user, 'authcate') and user.authcate != 'local':
        # For non-local auth (Firebase, OAuth, etc.), we shouldn't use this method
        # They should authenticate through their respective providers
        return False
    
    # For local users, verify the password
    if not hasattr(user, 'password') or user.password is None:
        # User doesn't have a password set
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


# async def get_current_user(db:Session= Depends(get_db), token = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     print(token)
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#     user = get_user_by_email(db, email=email)
#     if user is None:
#         raise credentials_exception
#     return user

async def get_current_user(req: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Method 1: Try JWT token from Authorization header
    auth_header = req.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        
        # Try custom JWT first
        email = try_jwt_authentication(token)
        if email:
            user = get_user_by_email(db, email=email)
            if user:
                return user
        
        # Try Firebase ID token as fallback
        email = verify_firebase_token(token)
        if email:
            user = get_user_by_email(db, email=email)
            if user:
                return user
    
    # Method 2: Try JWT token from cookies
    cookie_token = req.cookies.get("access_token")
    if cookie_token:
        # Try custom JWT first
        email = try_jwt_authentication(cookie_token)
        if email:
            user = get_user_by_email(db, email=email)
            if user:
                return user
        
        # Try Firebase ID token as fallback
        email = verify_firebase_token(cookie_token)
        if email:
            user = get_user_by_email(db, email=email)
            if user:
                return user


    # If all authentication methods fail, raise exception
    raise credentials_exception


def try_jwt_authentication(token: str):
    """
    Try to authenticate with custom JWT token
    Returns email if successful, None if failed
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None


def refresh_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        new_access_token = create_access_token(data={"sub": username})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
