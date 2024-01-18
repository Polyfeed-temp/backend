from datetime import timedelta

from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from fastapi import APIRouter, Request
from typing_extensions import Annotated
from .service import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user, UserResponse, refresh_token
from sqlalchemy.orm import Session
from src.database import get_db
from src.user.schemas import UserPydantic

router = APIRouter()

@router.post("/token", response_model=UserResponse)
async def login_for_access_token(response: Response,form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db),
):

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite='none')
    return {"user": user, "access_token": access_token}

@router.get("/verifyToken", response_model=UserPydantic)
async def verify_token(request: Request, current_user: UserPydantic = Depends(get_current_user)):
    headers = request.headers
    for key, value in headers.items():
        print(f"{key}: {value}")
    return current_user
@router.post("/refreshToken")
def refresh_token_route(token):
    return refresh_token(token)
