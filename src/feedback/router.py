from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.login.service import get_current_user
from .service import create_feedback,get_feedback_highlights_by_url
from .schemas import FeedbackBasePydantic, FeedbackWithHighlights


router = APIRouter()

@router.post("/", response_model=FeedbackBasePydantic)
def create_feedback_route(feedback:FeedbackBasePydantic, db: Session = Depends(get_db), user = Depends(get_current_user)):
    feedback.studentEmail = user.email
    return create_feedback(feedback, db)

# @router.get("/{feedbackId}", response_model=List[HighlightPydantic])
# def get_highlight_from_feedback_route(feedbackId: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
#     return get_highlights_from_feedback(feedbackId, db)

@router.get("/highlights")
def get_feedback_highlights_by_url_route( url, db: Session = Depends(get_db), user = Depends(get_current_user)):
    feedback = get_feedback_highlights_by_url(user, url, db)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

