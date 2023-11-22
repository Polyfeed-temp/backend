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


@router.post("/", response_model=UserPydantic)
def create_user(user: UserPydantic, db: Session = Depends(get_db)):
    print(user)
    return service.create_user(db, user)


@router.get("/{id_num}", response_model=UserPydantic)
def get_user_by_id(id_num: int, db: Session = Depends(get_db)):
    return service.get_user_by_id(db, id_num)


@router.patch("/{id_num}", response_model=UserPydantic)
def update_user_by_id(id_num: int, user: UserPydantic, db: Session = Depends(get_db)):
    return service.update_user(db, user, id_num)


@router.delete("/{id_num}", response_model=bool)
def delete_user_by_id(id_num: int, db: Session = Depends(get_db)):
    return service.delete_user(db, id_num)
