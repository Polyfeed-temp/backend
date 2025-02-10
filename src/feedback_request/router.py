from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.login.service import get_current_user
from .schemas import FeedbackRequestCreate, FeedbackRequestResponse
from .service import create_feedback_request, get_feedback_requests

router = APIRouter()

@router.post("/", response_model=FeedbackRequestResponse)
def create_request(
    request: FeedbackRequestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_feedback_request(db, request)

@router.get("/", response_model=List[FeedbackRequestResponse])
def get_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_feedback_requests(db, skip=skip, limit=limit) 