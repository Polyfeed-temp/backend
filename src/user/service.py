from sqlalchemy.orm import Session
from .models import User
from .schemas import UserPydantic
import json


def get_user_by_id(db: Session, userId: int):
    db_user = db.query(User).filter(User.id == userId).all()
    if len(db_user) == 1:
        return db_user
    else:
        return "Error: More than one user / No User found with the same ID."


def create_user(db: Session, userData: UserPydantic):
    db_user = User(**userData.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    return db.query(User).all()


def update_user(db: Session, userData: UserPydantic, userId: int):
    db_user = db.query(User).filter(User.id == userId).all()
    if len(db_user) == 1:
        for field, value in userData.model_dump().items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        return "Error: More than one user / No User found with the ID."


def delete_user(db: Session, userId: int):
    db_user = db.query(User).filter(User.id == userId).all()
    if len(db_user) == 1:
        db.delete(db_user)
        db.commit()
        return True
    else:
        return False
