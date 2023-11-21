from sqlalchemy.orm import Session
from .models import User
from .schemas import UserPydantic
import json


def get_user_by_id(db: Session, id_num: int):
    db_users = db.query(User).filter(User.id == id_num).all()
    if len(db_users) == 1:
        return db_users
    else:
        return "Error: More than one user found with the same ID."


def create_user(db: Session, user_data: UserPydantic):
    db_user = User(**user_data.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    return db.query(User).all()


