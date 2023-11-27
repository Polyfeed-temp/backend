from typing import List
from .schemas import UserPydantic
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.user import service

router = APIRouter()


@router.get("/all", response_model=List[UserPydantic])
def get_users(db: Session = Depends(get_db)):
    return service.get_users(db)


@router.post("/signup", response_model=UserPydantic)
def signup(user: UserPydantic, db: Session = Depends(get_db)):
    return service.signup_user(db, user)


@router.get("/{email}", response_model=UserPydantic)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    return service.get_user_by_email(db, email)


@router.patch("/{email}", response_model=UserPydantic)
def update_user_by_email(email: str, user: UserPydantic, db: Session = Depends(get_db)):
    return service.update_user(db, user, email)


@router.delete("/{email}", response_model=bool)
def delete_user_by_id(email: str, db: Session = Depends(get_db)):
    return service.delete_user(db, email)
