from sqlalchemy.orm import Session
from .models import Feedback
from .schemas import FeedbackBasePydantic, FeedbackWithHighlights
from src.highlight.models import Highlight
from src.action.models import AnnotationActionPoint
def get_feedback_by_assessment_id(assessment_id: int, db: Session):
    return db.query(Feedback).filter(Feedback.assessment_id == assessment_id).all()

def get_feedback_summumary_by_assessment_id(assessment_id: int, db: Session):
    return db.query(Feedback).join(Highlight, Feedback.highlight_id == Highlight.id).filter(Feedback.assessment_id == assessment_id).all()

def create_feedback(feedback:FeedbackBasePydantic, db: Session):
    feedback = Feedback(**feedback.model_dump())
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback

def get_highlights_from_feedback(feedback_id: int, db: Session):
    highlights = db.query(Highlight).filter(Highlight.feedbackId == feedback_id).all()
    return highlights

def get_feedback_highlights_by_url(user,url, db: Session):
    feedback_data = (
        db.query(Feedback, Highlight, AnnotationActionPoint)
        .join(Highlight, Feedback.id == Highlight.feedbackId)
        .join(Highlight.id == AnnotationActionPoint.highlightId)
        .filter(Highlight.url == url)
        .filter(Feedback.studentEmail == user.email)
        .all()
    )

    # Transform the results into the desired format
    feedback_highlights = []
    for feedback, highlight, action_point in feedback_data:
        feedback_dict = feedback.dict()
        highlight_dict = highlight.dict()

        # Assuming you have a relationship between Highlight and AnnotationActionPoint
        action_point_dict = action_point.dict()

        # Add action points to the highlight dictionary
        highlight_dict["actionPoints"] = [action_point_dict]

        # Add highlights to the feedback dictionary
        feedback_dict["highlights"] = [highlight_dict]

        feedback_highlights.append(feedback_dict)

    return feedback_highlights
