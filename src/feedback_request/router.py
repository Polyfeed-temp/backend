from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.login.service import get_current_user
from .schemas import FeedbackRequestPydantic
from .service import create_feedback_request, get_feedback_requests, get_feedback_request_by_assignment

router = APIRouter()

@router.post("/", response_model=FeedbackRequestPydantic)
def create_request(
    request: FeedbackRequestPydantic,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_feedback_request(db, request, student_id=current_user.email)

@router.get("/", response_model=List[FeedbackRequestPydantic])
def get_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_feedback_requests(db, student_id=current_user.email, skip=skip, limit=limit)

@router.get("/{assignment_id}", response_model=FeedbackRequestPydantic)
def get_request_by_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get feedback request for a specific assignment"""
    return get_feedback_request_by_assignment(db, assignment_id, current_user.email) 