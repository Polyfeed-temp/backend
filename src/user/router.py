from typing import List, Union
from .schemas import UserPydantic, EnrolledUnitPydantic, UserSignupRequest, PasswordResetRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.user import service

from src.user.schemas import UserPydantic
from src.login.service import get_current_user
router = APIRouter()


@router.get("/all", response_model=List[UserPydantic])
def get_users(db: Session = Depends(get_db)):
    return service.get_users(db)


@router.post("/signup", response_model=UserPydantic)
def signup(user: UserSignupRequest, db: Session = Depends(get_db)):

    result = service.signup_user(db, user)
    if result:
        return result
    elif result is None:
        raise HTTPException(status_code=400, detail="Email and password are required and cannot be empty")
    else:
        raise HTTPException(status_code=409, detail="User already exists")

@router.post("/create", response_model=UserPydantic)
def create_user(user: UserPydantic, db: Session = Depends(get_db)):
    return service.create_user(db, user)


@router.post("/reset-password")
def reset_password(
    password_reset: PasswordResetRequest,
    current_user: UserPydantic = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = service.reset_password(
        db, 
        current_user.email, 
        password_reset.old_password, 
        password_reset.new_password
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"message": result["message"]}


#
@router.get("/{email}", response_model=Union[UserPydantic, None])
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    return service.get_user_by_email(db, email)
#
#
# @router.patch("/{email}", response_model=UserPydantic)
# def update_user_by_email(email: str, user: UserPydantic, db: Session = Depends(get_db)):
#     return service.update_user(db, user, email)
#
#
# @router.delete("/{email}", response_model=bool)
# def delete_user_by_id(email: str, db: Session = Depends(get_db)):
#     return service.delete_user(db, email)
#
# @router.get("/student/enrolledUnits", response_model=List[EnrolledUnitPydantic])
# def get_student_all_student_enrolled_units(current_user: UserPydantic = Depends(get_current_user), db: Session = Depends(get_db)):
#     student_email = current_user.email
#     return service.get_student_all_student_enrolled_units(db, student_email)