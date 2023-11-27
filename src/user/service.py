from sqlalchemy.orm import Session
from .models import User
from .schemas import UserPydantic
from src.dependencies import get_password_hash


def get_user_by_email(db: Session, email: str):
    db_user = db.query(User).filter(User.email == email).all()
    if len(db_user) == 1:
        return db_user[0]
    else:
        return None


def create_user(db: Session, userData: UserPydantic):
    db_user = User(**userData.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def signup_user(db: Session, userData: UserPydantic):
    db_user = db.query(User).filter(User.monashId == userData.monashId).all()
    if len(db_user) == 1:
        return "Error: User already exists."
    else:
        #hash the password
        userData.password = get_password_hash(userData.password)
        userData.role= userData.role.value

        return create_user(db, userData)
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
