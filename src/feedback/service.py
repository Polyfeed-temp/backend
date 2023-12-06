from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .models import Feedback
from .schemas import FeedbackBasePydantic, FeedbackWithHighlights
from src.highlight.models import Highlight
from src.highlight.schemas import HighlightPydantic
from src.action.models import AnnotationActionPoint
import json

from ..highlight.schemas import CompleteHighlight


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


def get_feedback_highlights_by_url(user, url, db: Session):
    print(f'url {url}')


    query = (
        db.query(Feedback, Highlight, func.concat('[', func.group_concat(
            func.json_object(
                'id', AnnotationActionPoint.id,
                'action', AnnotationActionPoint.action,
                'category', AnnotationActionPoint.category,
                'deadline', AnnotationActionPoint.deadline
            )
        ), ']').label('actionItems')).outerjoin(Highlight, Feedback.id == Highlight.feedbackId).outerjoin(AnnotationActionPoint, Highlight.id == AnnotationActionPoint.highlightId).filter(Feedback.url == url).filter(Feedback.studentEmail == user.email).group_by(Feedback.id, Highlight.id))

    result = query.all()
    feedbackHighlights =[]
    feedback =None
    if len(result) == 0:
        return None
    for row in result:
        feedback, highlight, actionItems = row
        print(feedback)
        if not highlight:
            break

        temp = HighlightPydantic(id=highlight.id, startMeta=json.loads(highlight.startMeta), endMeta=json.loads(highlight.endMeta), text=highlight.text, annotationTag=highlight.annotationTag, notes=highlight.notes, feedbackId=highlight.feedbackId)
        if actionItems:
            complete_highlight= {'annotation' : temp, 'actionItems':json.loads(actionItems)}
        feedbackHighlights.append(complete_highlight)



    return {"id":feedback.id,"url":feedback.url, "assessmentId": feedback.assessmentId, "studentEmail":feedback.studentEmail,
            "mark": feedback.mark,"highlights":feedbackHighlights}

