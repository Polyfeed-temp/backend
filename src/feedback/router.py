from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from src.database import get_db
from src.login.service import get_current_user
from .service import create_feedback,get_feedback_highlights_by_url, get_all_user_feedback_highlights, rate_feedback, delete_feedback, delete_all_highlights,patch_assessment_feedback, rate_gpt_response, get_feeedbacks_by_assessment_id, get_feedbacks_by_user_email, get_feeedbacks_by_unitcode_assessment
from .schemas import FeedbackBasePydantic,FeedbackRating


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

@router.get("/all")
def get_all_user_feedback_highlights_route(db: Session = Depends(get_db), user = Depends(get_current_user)):
    feedback = get_all_user_feedback_highlights(user, db)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.post("/rate/{feedbackId}")
def rate_feedback_route(feedbackId, rating:FeedbackRating,db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not rate_feedback(feedbackId, rating, db, user):
        raise HTTPException(status_code=404, detail="Feedback not found")
    return True


@router.get("/feedback/{unit_code}/{assessment_name}")
def get_feedbacks_by_assessment_id_route(unit_code: str, assessment_name: str, db: Session = Depends(get_db)):
    feedback = get_feeedbacks_by_unitcode_assessment(unit_code, assessment_name, db)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@router.get("/feedbacks/{email}")
def rate_feedback_route(email,db: Session = Depends(get_db)):
    feedback = get_feedbacks_by_user_email(email, db)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@router.delete("/{feedbackId}")
def delete_feedback_route(feedbackId, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not delete_feedback(feedbackId, db, user):
        raise HTTPException(status_code=404, detail="Feedback not found")
    return True

@router.delete("/all/{feedbackId}")
def delete_all_highlights_route(feedbackId, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not delete_all_highlights(feedbackId, db, user):
        raise HTTPException(status_code=404, detail="Feedback not found")
    return True

@router.patch("/assessment/{feedback_id}/{assessment_id}")
def patch_assessment_feedback_route(feedback_id, assessment_id, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not patch_assessment_feedback(feedback_id, assessment_id, db, user):
        raise HTTPException(status_code=404, detail="Feedback not found")
    return True

@router.post("/rate/gpt/{feedbackId}")
def rate_gpt_response_route(feedbackId, rating:int, attemptTime:int,db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not rate_gpt_response(feedbackId, rating, db, user,attemptTime):
        raise HTTPException(status_code=404, detail="Feedback not found")
    return True

@router.get("/assessment/{assessment_id}")
def get_feedbacks_by_assessment_id_route(assessment_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    feedback = get_feeedbacks_by_assessment_id(assessment_id, db, user)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

