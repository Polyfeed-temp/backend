from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from .models import Feedback
from src.unit.service import get_all_units_with_assessments
from .schemas import FeedbackBasePydantic, FeedbackRating
from src.highlight.models import Highlight
from src.highlight.schemas import HighlightPydantic
from src.action.models import AnnotationActionPoint
import json
from src.database import unit as unit_temp


def get_feedback_by_assessment_id(assessment_id: int, db: Session):
    return db.query(Feedback).filter(Feedback.assessment_id == assessment_id).all()

def get_feedback_summumary_by_assessment_id(assessment_id: int, db: Session):
    return db.query(Feedback).join(Highlight, Feedback.highlight_id == Highlight.id).filter(Feedback.assessment_id == assessment_id).all()

def create_feedback(feedback:FeedbackBasePydantic, db: Session):
    feedback.url = str(feedback.url)
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

    cached_units_data = unit_temp.get_data()
    if not cached_units_data:
        cached_units_data = unit_temp.insert_data(get_all_units_with_assessments(db))
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
            complete_highlight= {'annotation' : temp, 'actionItems':    [value for value in json.loads(actionItems) if value["action"] != None ]}
        feedbackHighlights.append(complete_highlight)
    unit_code = None
    assessment_name = None
    if cached_units_data:
        for unit_data in cached_units_data:
            assessments = unit_data.get('assessments')
            if assessments:
                for assessment in assessments:
                    if assessment['id'] == feedback.assessmentId:
                        unit_code = unit_data['unitCode'] +unit_data['year'] + unit_data['semester']
                        assessment_name = assessment['assessmentName']

                        break


    return {"id":feedback.id,"url":feedback.url, "assessmentId": feedback.assessmentId, "studentEmail":feedback.studentEmail, "clarity": feedback.clarity, "evaluativeJudgement": feedback.evaluativeJudgement, "personalise": feedback.personalise, "usability": feedback.usability, "emotion": feedback.emotion,
            "mark": feedback.mark,"highlights":feedbackHighlights, "unitCode":unit_code, "assessmentName":assessment_name}

def get_all_user_feedback_highlights(user, db: Session):
    cached_units_data = unit_temp.get_data()
    if not cached_units_data:
        cached_units_data = unit_temp.insert_data(get_all_units_with_assessments(db))
    query = (
        db.query(Feedback, Highlight, func.concat('[', func.group_concat(
            func.json_object(
                'id', AnnotationActionPoint.id,
                'action', AnnotationActionPoint.action,
                'category', AnnotationActionPoint.category,
                'deadline', AnnotationActionPoint.deadline
            )
        ), ']').label('actionItems')).outerjoin(Highlight, Feedback.id == Highlight.feedbackId).outerjoin(AnnotationActionPoint, Highlight.id == AnnotationActionPoint.highlightId).filter(Feedback.studentEmail == user.email).group_by(Feedback.id, Highlight.id))

    result = query.all()
    feedbackHighlights =[]
    feedbacks_dict={}
    if len(result) == 0:
        return None
    for row in result:
        feedback, highlight, actionItems = row
        feedback_entry = feedbacks_dict.setdefault(feedback.id, {
            "id": feedback.id, "url": feedback.url, "assessmentId": feedback.assessmentId,
            "studentEmail": feedback.studentEmail, "mark": feedback.mark, "highlights": []
        })

        if cached_units_data:
            for unit_data in cached_units_data:
                assessments = unit_data.get('assessments')
                if assessments:
                    for assessment in assessments:
                        if assessment['id'] == feedback.assessmentId:
                            feedbacks_dict[feedback.id]['unitCode'] = unit_data['unitCode'] +unit_data['year'] + unit_data['semester']
                            feedbacks_dict[feedback.id]['assessmentName'] = assessment['assessmentName']

                            break

        if highlight:
            highlight_data = HighlightPydantic(
                id=highlight.id, startMeta=json.loads(highlight.startMeta),
                endMeta=json.loads(highlight.endMeta), text=highlight.text,
                annotationTag=highlight.annotationTag, notes=highlight.notes,
                feedbackId=highlight.feedbackId
            )
            filtered_action_items = json.loads(actionItems)
            complete_highlight = {
                'annotation': highlight_data,
                'actionItems':  [value for value in filtered_action_items if value["action"] != None ]
            }
            feedback_entry['highlights'].append(complete_highlight)
    feedbacks_list = list(feedbacks_dict.values())
    return feedbacks_list

def rate_feedback(feedbackId:int, rating:FeedbackRating,db: Session, user):

        feedback = db.query(Feedback).filter(Feedback.id == feedbackId).first()

        if feedback and feedback.studentEmail == user.email:
            feedback.clarity = rating.clarity
            feedback.evaluativeJudgement = rating.evaluativeJudgement
            feedback.personalise = rating.personalise
            feedback.usability = rating.usability
            feedback.emotion = rating.emotion
            db.commit()
            return True
        else:
            return False
def rate_gpt_response(feedbackId:int, rating:int,db: Session, user):

        feedback = db.query(Feedback).filter(Feedback.id == feedbackId).first()

        if feedback and feedback.studentEmail == user.email:
            feedback.gptResponseRating = rating
            db.commit()
            return True
        else:
            return False

def delete_feedback(feedbackId, db: Session, user):
    feedback = db.query(Feedback).filter(Feedback.id == feedbackId).first()
    if feedback and feedback.studentEmail == user.email:
        db.delete(feedback)
        db.commit()
        return True
    else:
        return False

def delete_all_highlights(feedbackId, db: Session, user):
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedbackId).first()
        if feedback and feedback.studentEmail == user.email:
            highlights = db.query(Highlight).filter(Highlight.feedbackId == feedbackId).all()
            for highlight in highlights:
                db.delete(highlight)

                db.commit()
            return True
        else:
            return False
    except SQLAlchemyError as e:
        db.rollback()  # Rollback in case of any error
        print(f"An error occurred: {e}")
        return False

def patch_assessment_feedback(feedback_id, assessment_id, db: Session, user):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if feedback and feedback.studentEmail == user.email:
        feedback.assessmentId = assessment_id
        db.commit()
        return True
    else:
        return False