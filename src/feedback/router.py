from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.login.service import get_current_user
from .service import create_feedback, get_feedback_by_assessment_id, get_highlights_from_feedback
from .schemas import FeedbackPydantic
from src.highlight.schemas import HighlightPydantic

router = APIRouter()

@router.post("/", response_model=FeedbackPydantic)
def create_feedback_route(feedback:FeedbackPydantic, db: Session = Depends(get_db), user = Depends(get_current_user)):
    feedback.studentEmail = user.email
    print(feedback)
    return create_feedback(feedback, db)

@router.get("/{feedbackId}", response_model=List[HighlightPydantic])
def get_highlight_from_feedback_route(feedbackId: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return get_highlights_from_feedback(feedbackId, db)