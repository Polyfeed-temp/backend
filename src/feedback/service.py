from sqlalchemy.orm import Session
from .models import Feedback
from .schemas import FeedbackPydantic
from src.highlight.models import Highlight
def get_feedback_by_assessment_id(assessment_id: int, db: Session):
    return db.query(Feedback).filter(Feedback.assessment_id == assessment_id).all()

def get_feedback_summumary_by_assessment_id(assessment_id: int, db: Session):
    return db.query(Feedback).join(Highlight, Feedback.highlight_id == Highlight.id).filter(Feedback.assessment_id == assessment_id).all()

def create_feedback(feedback:FeedbackPydantic, db: Session):
    feedback = Feedback(**feedback.model_dump())
    db.add(feedback)
    db.commit()
    db.refresh(feedback)


    return feedback

def get_highlights_from_feedback(feedback_id: int, db: Session):
    highlights = db.query(Highlight).filter(Highlight.feedbackId == feedback_id).all()
    return highlights