from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from .models import Feedback
from src.unit.service import get_all_units_with_assessments
from .schemas import FeedbackBasePydantic, FeedbackRating
from src.highlight.models import Highlight
from src.highlight.schemas import HighlightPydantic
from src.action.models import AnnotationActionPoint
from src.highlight.schemas import DomMeta
import json
from src.database import unit as unit_temp
from src.assessment.models import Assessment
from src.user.encryption import encrypt_field, decrypt_field


def _encrypt_feedback_emails(feedback_data: dict) -> dict:
    """Encrypt email fields in feedback data before storage."""
    encrypted_data = feedback_data.copy()
    
    # Encrypt email fields
    if 'studentEmail' in encrypted_data and encrypted_data['studentEmail']:
        encrypted_data['studentEmail'] = encrypt_field(encrypted_data['studentEmail'])
    
    if 'markerEmail' in encrypted_data and encrypted_data['markerEmail']:
        encrypted_data['markerEmail'] = encrypt_field(encrypted_data['markerEmail'])
    
    return encrypted_data


def _decrypt_feedback_emails(feedback_obj) -> dict:
    """Decrypt email fields when retrieving feedback from database."""
    if hasattr(feedback_obj, '__dict__'):
        # Convert SQLAlchemy object to dict
        data_dict = {column.name: getattr(feedback_obj, column.name) for column in feedback_obj.__table__.columns}
    elif hasattr(feedback_obj, '_asdict'):
        # SQLAlchemy Row object
        data_dict = feedback_obj._asdict()
    elif hasattr(feedback_obj, 'keys'):
        # Dict-like object
        data_dict = dict(feedback_obj)
    else:
        # Convert to dict manually
        data_dict = {}
        for key in dir(feedback_obj):
            if not key.startswith('_'):
                try:
                    data_dict[key] = getattr(feedback_obj, key)
                except:
                    pass
    
    # Decrypt email fields
    if 'studentEmail' in data_dict and data_dict['studentEmail']:
        try:
            data_dict['studentEmail'] = decrypt_field(data_dict['studentEmail'])
        except:
            pass  # If decryption fails, keep original value
    
    if 'markerEmail' in data_dict and data_dict['markerEmail']:
        try:
            data_dict['markerEmail'] = decrypt_field(data_dict['markerEmail'])
        except:
            pass  # If decryption fails, keep original value
    
    return data_dict


def _find_feedback_by_encrypted_email(db: Session, email: str, url: str = None) -> Feedback:
    """Find feedback by searching through encrypted emails."""
    query = db.query(Feedback)
    if url:
        query = query.filter(Feedback.url == url)
    
    feedbacks = query.all()
    
    for feedback in feedbacks:
        try:
            decrypted_email = decrypt_field(feedback.studentEmail)
            if decrypted_email == email:
                return feedback
        except:
            # If decryption fails, check if it's already unencrypted
            if feedback.studentEmail == email:
                return feedback
    
    return None


def get_feedback_by_assessment_id(assessment_id: int, db: Session):
    return db.query(Feedback).filter(Feedback.assessment_id == assessment_id).all()

def get_feedback_summumary_by_assessment_id(assessment_id: int, db: Session):
    return db.query(Feedback).join(Highlight, (Feedback.highlight_id == Highlight.id) & (Highlight.rowStatus == "ACTIVE")).filter(Feedback.assessment_id == assessment_id).all()

def create_feedback(feedback:FeedbackBasePydantic, db: Session):
    try:
        print("feedback", feedback)
        feedback_dict = feedback.model_dump()
        # Ensure feedbackUseful is never None
        feedback_dict['feedbackUseful'] = feedback_dict.get('feedbackUseful') or ''
        feedback_dict['url'] = str(feedback.url)
        
        # Encrypt email fields before storage
        encrypted_feedback_dict = _encrypt_feedback_emails(feedback_dict)
        
        feedback_model = Feedback(**encrypted_feedback_dict)
        db.add(feedback_model)
        db.commit()
        db.refresh(feedback_model)
        
        # Return decrypted data for response
        return _decrypt_feedback_emails(feedback_model)
    except SQLAlchemyError as e:
        print("error in creating feedback" , e)
        db.rollback()  # Add rollback here
        
        # Find existing feedback using encrypted email search
        update_feedback = _find_feedback_by_encrypted_email(db, feedback.studentEmail, str(feedback.url))
        if update_feedback:
            return _decrypt_feedback_emails(update_feedback)
        return None

def get_highlights_from_feedback(feedback_id: int, db: Session):
    highlights = db.query(Highlight).filter(Highlight.feedbackId == feedback_id, Highlight.rowStatus == "ACTIVE").all()
    return highlights


def get_feedback_highlights_by_url(user, url, db: Session):
    main_url = url.split('#')[0]
    cached_units_data = get_all_units_with_assessments(db)
    
    # Find feedback using encrypted email search
    user_feedback = _find_feedback_by_encrypted_email(db, user['email'], main_url)
    if not user_feedback:
        return None
    
    query = (
        db.query(Feedback, Highlight, func.concat('[', func.group_concat(
            func.json_object(
                'id', AnnotationActionPoint.id,
                'action', AnnotationActionPoint.action,
                'category', AnnotationActionPoint.category,
                'deadline', AnnotationActionPoint.deadline,
                'status', AnnotationActionPoint.status,
            )
        ), ']').label('actionItems')).outerjoin(Highlight, (Feedback.id == Highlight.feedbackId) & 
                                                (Highlight.rowStatus == "ACTIVE"))
        .outerjoin(AnnotationActionPoint,( Highlight.id == AnnotationActionPoint.highlightId) 
                   & (AnnotationActionPoint.rowStatus == "ACTIVE"))
        .filter(Feedback.url == main_url).filter(Feedback.id == user_feedback.id, 
                                                 Feedback.rowStatus == "ACTIVE")
        .group_by(Feedback.id, Highlight.id))

    result = query.all()
    feedbackHighlights =[]
    feedback =None
    if len(result) == 0:
        return None
    for row in result:
        feedback, highlight, actionItems = row

        if not highlight:
            break
        start_meta = highlight.startMeta
        end_meta = highlight.endMeta

        parsed_start_meta = json.loads(start_meta) if start_meta is not None else DomMeta(parentTagName="div", parentIndex=0, textOffset=0)
        parsed_end_meta = json.loads(end_meta) if end_meta is not None else DomMeta(parentTagName="div", parentIndex=0, textOffset=0)
        temp = HighlightPydantic(id=highlight.id, startMeta=parsed_start_meta, endMeta=parsed_end_meta, text=highlight.text, annotationTag=highlight.annotationTag, notes=highlight.notes, feedbackId=highlight.feedbackId)
        if actionItems:
            complete_highlight= {'annotation' : temp, 'actionItems':    [value for value in json.loads(actionItems) if value["action"] != None ]}
        feedbackHighlights.append(complete_highlight)
    
    # Decrypt feedback data for response
    decrypted_feedback = _decrypt_feedback_emails(feedback)
    
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

    return {"id":decrypted_feedback["id"],"url":decrypted_feedback["url"], "assessmentId": decrypted_feedback["assessmentId"], "studentEmail":decrypted_feedback["studentEmail"], "performance": decrypted_feedback.get("performance"), "clarity": decrypted_feedback.get("clarity"), "evaluativeJudgement": decrypted_feedback.get("evaluativeJudgement"), "personalise": decrypted_feedback.get("personalise"), "usability": decrypted_feedback.get("usability"), "emotion": decrypted_feedback.get("emotion"),
                "mark": decrypted_feedback["mark"],"unitCode":unit_code, "assessmentName":assessment_name, 
                    "gptResponseRating":decrypted_feedback.get("gptResponseRating"), "gptQueryText": decrypted_feedback.get("gptQueryText"),"gptResponse":decrypted_feedback.get("gptResponse"), 
                    "gptResponseRating_2":decrypted_feedback.get("gptResponseRating_2"), "gptQueryText_2": decrypted_feedback.get("gptQueryText_2"),"gptResponse_2":decrypted_feedback.get("gptResponse_2"), 
                    "highlights":feedbackHighlights, "furtherQuestions":decrypted_feedback.get("furtherQuestions"), "comment":decrypted_feedback.get("comment") }

def get_all_user_feedback_highlights(user, db: Session):
    cached_units_data = get_all_units_with_assessments(db)
    
    # Get all feedbacks for user using encrypted email search
    all_feedbacks = db.query(Feedback).filter(Feedback.rowStatus == "ACTIVE").all()
    user_feedbacks = []
    
    for feedback in all_feedbacks:
        try:
            decrypted_email = decrypt_field(feedback.studentEmail)
            if decrypted_email == user['email']:
                user_feedbacks.append(feedback.id)
        except:
            # If decryption fails, check if it's already unencrypted
            if feedback.studentEmail == user['email']:
                user_feedbacks.append(feedback.id)
    
    if not user_feedbacks:
        return None
    
    query = (
        db.query(Feedback, Highlight, func.concat('[', func.group_concat(
            func.json_object(
                'id', AnnotationActionPoint.id,
                'action', AnnotationActionPoint.action,
                'category', AnnotationActionPoint.category,
                'deadline', AnnotationActionPoint.deadline,
                'status', AnnotationActionPoint.status
            )
        ), ']').label('actionItems')).outerjoin(Highlight, (Feedback.id == Highlight.feedbackId) & (Highlight.rowStatus == "ACTIVE"))
            .outerjoin(AnnotationActionPoint, (Highlight.id == AnnotationActionPoint.highlightId) &
                       ((AnnotationActionPoint.rowStatus == "ACTIVE")))
            .filter(Feedback.id.in_(user_feedbacks), Feedback.rowStatus == "ACTIVE")
            .group_by(Feedback.id, Highlight.id))

    result = query.all()
    feedbacks_dict={}
    if len(result) == 0:
        return None
    
    for row in result:
        feedback, highlight, actionItems = row
        
        # Decrypt feedback data
        decrypted_feedback = _decrypt_feedback_emails(feedback)
        
        feedback_entry = feedbacks_dict.setdefault(feedback.id, {
            "id": decrypted_feedback["id"], "url": decrypted_feedback["url"], "assessmentId": decrypted_feedback["assessmentId"],
            "studentEmail": decrypted_feedback["studentEmail"], "mark": decrypted_feedback["mark"], "highlights": []
        })

        if cached_units_data:
            for unit_data in cached_units_data:
                assessments = unit_data.get('assessments')
                if assessments:
                    for assessment in assessments:
                        if assessment['id'] == feedback.assessmentId:
                            feedbacks_dict[feedback.id]['unitCode'] = unit_data['id']
                            feedbacks_dict[feedback.id]['year'] = unit_data['year']
                            feedbacks_dict[feedback.id]['semester'] = unit_data['semester']
                            feedbacks_dict[feedback.id]['assessmentName'] = assessment['assessmentName']

                            break

        if highlight:
            start_meta = highlight.startMeta
            end_meta = highlight.endMeta

            parsed_start_meta = json.loads(start_meta) if start_meta is not None else DomMeta(parentTagName="div",
                                                                                              parentIndex=0,
                                                                                              textOffset=0)
            parsed_end_meta = json.loads(end_meta) if end_meta is not None else DomMeta(parentTagName="div",
                                                                                        parentIndex=0, textOffset=0)
            highlight_data = HighlightPydantic(
                id=highlight.id, startMeta=parsed_start_meta,
                endMeta=parsed_end_meta, text=highlight.text,
                annotationTag=highlight.annotationTag, notes=highlight.notes,
                feedbackId=highlight.feedbackId,
                commonTheme=highlight.commonTheme
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

    if feedback:
        # Check if user owns this feedback by decrypting email
        try:
            decrypted_email = decrypt_field(feedback.studentEmail)
            user_owns_feedback = (decrypted_email == user['email'])
        except:
            # If decryption fails, check if it's already unencrypted
            user_owns_feedback = (feedback.studentEmail == user['email'])
        
        if user_owns_feedback:
            feedback.performance = rating.performance
            feedback.clarity = rating.clarity
            feedback.evaluativeJudgement = rating.evaluativeJudgement
            feedback.personalise = rating.personalise
            feedback.usability = rating.usability
            feedback.emotion = rating.emotion
            feedback.furtherQuestions = rating.furtherQuestions
            feedback.comment = rating.comment
            db.commit()
            return True
    
    return False
        
def rate_gpt_response(feedbackId:int, rating:int,db: Session, user,attemptTime):
    feedback = db.query(Feedback).filter(Feedback.id == feedbackId).first()

    if feedback:
        # Check if user owns this feedback by decrypting email
        try:
            decrypted_email = decrypt_field(feedback.studentEmail)
            user_owns_feedback = (decrypted_email == user['email'])
        except:
            # If decryption fails, check if it's already unencrypted
            user_owns_feedback = (feedback.studentEmail == user['email'])
        
        if user_owns_feedback:
            if attemptTime ==1 :
                feedback.gptResponseRating = rating
            else:
                feedback.gptResponseRating_2 = rating
            db.commit()
            return True
    
    return False

def delete_feedback(feedbackId, db: Session, user):
    feedback = db.query(Feedback).filter(Feedback.id == feedbackId).first()
    if feedback:
        # Check if user owns this feedback by decrypting email
        try:
            decrypted_email = decrypt_field(feedback.studentEmail)
            user_owns_feedback = (decrypted_email == user['email'])
        except:
            # If decryption fails, check if it's already unencrypted
            user_owns_feedback = (feedback.studentEmail == user['email'])
        
        if user_owns_feedback:
            feedback.rowStatus = "INACTIVE"
            db.commit()
            return True
    
    return False

def delete_all_highlights(feedbackId, db: Session, user):
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedbackId).first()
        if feedback:
            # Check if user owns this feedback by decrypting email
            try:
                decrypted_email = decrypt_field(feedback.studentEmail)
                user_owns_feedback = (decrypted_email == user['email'])
            except:
                # If decryption fails, check if it's already unencrypted
                user_owns_feedback = (feedback.studentEmail == user['email'])
            
            if user_owns_feedback:
                highlights = db.query(Highlight).filter(Highlight.feedbackId == feedbackId, Highlight.rowStatus == "ACTIVE").all()
                for highlight in highlights:
                    highlight.rowStatus = "INACTIVE"
                    db.commit()
                return True
        return False
    except SQLAlchemyError as e:
        db.rollback()  # Rollback in case of any error
        print(f"An error occurred: {e}")
        return False

def patch_assessment_feedback(feedback_id, assessment_id, db: Session, user):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if feedback:
        # Check if user owns this feedback by decrypting email
        try:
            decrypted_email = decrypt_field(feedback.studentEmail)
            user_owns_feedback = (decrypted_email == user['email'])
        except:
            # If decryption fails, check if it's already unencrypted
            user_owns_feedback = (feedback.studentEmail == user['email'])
        
        if user_owns_feedback:
            feedback.assessmentId = assessment_id
            db.commit()
            return True
    
    return False

def get_feeedbacks_by_assessment_id(assessment_id, db: Session, user):
    cached_units_data = unit_temp.get_data()
    if not cached_units_data:
        cached_units_data = unit_temp.insert_data(get_all_units_with_assessments(db))
    query = (
        db.query(Feedback, Highlight, func.concat('[', func.group_concat(
            func.json_object(
                'id', AnnotationActionPoint.id,
                'action', AnnotationActionPoint.action,
                'category', AnnotationActionPoint.category,
                'deadline', AnnotationActionPoint.deadline,
                'status', AnnotationActionPoint.status
            )
        ), ']').label('actionItems'))
            .outerjoin(Highlight, (Feedback.id == Highlight.feedbackId) & (Highlight.rowStatus == "ACTIVE"))
            .outerjoin(AnnotationActionPoint, (Highlight.id == AnnotationActionPoint.highlightId) & 
                       (AnnotationActionPoint.rowStatus == "ACTIVE"))
            .filter(Feedback.assessmentId == assessment_id, Feedback.rowStatus == "ACTIVE")
            .group_by(Feedback.id, Highlight.id))

    result = query.all()
    feedbackHighlights = []
    feedback = None
    
    # Filter results by decrypted email to find user's feedback
    user_feedback_found = False
    for row in result:
        temp_feedback, highlight, actionItems = row
        
        # Check if this feedback belongs to the user
        try:
            decrypted_email = decrypt_field(temp_feedback.studentEmail)
            if decrypted_email == user['email']:
                feedback = temp_feedback
                user_feedback_found = True
                break
        except:
            # If decryption fails, check if it's already unencrypted
            if temp_feedback.studentEmail == user['email']:
                feedback = temp_feedback
                user_feedback_found = True
                break
    
    if not user_feedback_found:
        return None
    
    # Now get all highlights for this specific feedback
    highlight_query = (
        db.query(Feedback, Highlight, func.concat('[', func.group_concat(
            func.json_object(
                'id', AnnotationActionPoint.id,
                'action', AnnotationActionPoint.action,
                'category', AnnotationActionPoint.category,
                'deadline', AnnotationActionPoint.deadline,
                'status', AnnotationActionPoint.status
            )
        ), ']').label('actionItems'))
            .outerjoin(Highlight, (Feedback.id == Highlight.feedbackId) & (Highlight.rowStatus == "ACTIVE"))
            .outerjoin(AnnotationActionPoint, (Highlight.id == AnnotationActionPoint.highlightId) & 
                       (AnnotationActionPoint.rowStatus == "ACTIVE"))
            .filter(Feedback.id == feedback.id, Feedback.rowStatus == "ACTIVE")
            .group_by(Feedback.id, Highlight.id))
    
    highlight_results = highlight_query.all()
    
    if len(highlight_results) == 0:
        return None
        
    for row in highlight_results:
        feedback, highlight, actionItems = row

        if not highlight:
            break
        start_meta = highlight.startMeta
        end_meta = highlight.endMeta

        parsed_start_meta = json.loads(start_meta) if start_meta is not None else DomMeta(parentTagName="div",
                                                                                          parentIndex=0, textOffset=0)
        parsed_end_meta = json.loads(end_meta) if end_meta is not None else DomMeta(parentTagName="div", parentIndex=0,
                                                                                    textOffset=0)
        temp = HighlightPydantic(id=highlight.id, startMeta=parsed_start_meta, endMeta=parsed_end_meta,
                                 text=highlight.text, annotationTag=highlight.annotationTag, notes=highlight.notes,
                                 feedbackId=highlight.feedbackId)
        if actionItems:
            complete_highlight = {'annotation': temp, 'actionItems': [value for value in json.loads(actionItems) if
                                                                      value["action"] != None]}
        feedbackHighlights.append(complete_highlight)
   
    unit_code = None
    assessment_name = None
    if cached_units_data:
        for unit_data in cached_units_data:
            assessments = unit_data.get('assessments')
            if assessments:
                for assessment in assessments:
                    if assessment['id'] == feedback.assessmentId:
                        unit_code = unit_data['unitCode'] + unit_data['year'] + unit_data['semester']
                        assessment_name = assessment['assessmentName']
                        break

    # Decrypt feedback data for response
    decrypted_feedback = _decrypt_feedback_emails(feedback)
    
    return {"id": decrypted_feedback["id"], "url": decrypted_feedback["url"], "assessmentId": decrypted_feedback["assessmentId"],
            "studentEmail": decrypted_feedback["studentEmail"], "performance": decrypted_feedback.get("performance"), "clarity": decrypted_feedback.get("clarity"),
            "evaluativeJudgement": decrypted_feedback.get("evaluativeJudgement"), "personalise": decrypted_feedback.get("personalise"),
            "usability": decrypted_feedback.get("usability"), "emotion": decrypted_feedback.get("emotion"),
            "mark": decrypted_feedback.get("mark"), "unitCode": unit_code, "assessmentName": assessment_name,
            "gptResponseRating": decrypted_feedback.get("gptResponseRating"), "gptQueryText": decrypted_feedback.get("gptQueryText"),
            "gptResponse": decrypted_feedback.get("gptResponse"), "highlights": feedbackHighlights, }



def get_feedbacks_by_user_email(email, db: Session):
    cached_units_data = get_all_units_with_assessments(db)
    
    # Get all feedbacks for user using encrypted email search
    all_feedbacks = db.query(Feedback).filter(Feedback.rowStatus == "ACTIVE").all()
    user_feedbacks = []
    
    for feedback in all_feedbacks:
        try:
            decrypted_email = decrypt_field(feedback.studentEmail)
            if decrypted_email == email:
                user_feedbacks.append(feedback.id)
        except:
            # If decryption fails, check if it's already unencrypted
            if feedback.studentEmail == email:
                user_feedbacks.append(feedback.id)
    
    if not user_feedbacks:
        return None
    
    query = (
        db.query(Feedback, Highlight, func.concat('[', func.group_concat(
            func.json_object(
                'id', AnnotationActionPoint.id,
                'action', AnnotationActionPoint.action,
                'category', AnnotationActionPoint.category,
                'deadline', AnnotationActionPoint.deadline,
                'status', AnnotationActionPoint.status
            )
        ), ']').label('actionItems')).outerjoin(Highlight, (Feedback.id == Highlight.feedbackId) & (Highlight.rowStatus == "ACTIVE"))
            .outerjoin(AnnotationActionPoint, (Highlight.id == AnnotationActionPoint.highlightId) &
                       ((AnnotationActionPoint.rowStatus == "ACTIVE")))
            .filter(Feedback.id.in_(user_feedbacks), Feedback.rowStatus == "ACTIVE")
            .group_by(Feedback.id, Highlight.id))

    result = query.all()
    feedbacks_dict={}
    if len(result) == 0:
        return None
    
    for row in result:
        feedback, highlight, actionItems = row
        
        # Decrypt feedback data
        decrypted_feedback = _decrypt_feedback_emails(feedback)
        
        feedback_entry = feedbacks_dict.setdefault(feedback.id, {
            "id": decrypted_feedback["id"], "url": decrypted_feedback["url"], "assessmentId": decrypted_feedback["assessmentId"],
            "studentEmail": decrypted_feedback["studentEmail"], "mark": decrypted_feedback["mark"], 
            "performance": decrypted_feedback.get("performance"), "clarity": decrypted_feedback.get("clarity"), "evaluativeJudgement": decrypted_feedback.get("evaluativeJudgement"), 
            "personalise": decrypted_feedback.get("personalise"), "usability": decrypted_feedback.get("usability"), "emotion": decrypted_feedback.get("emotion"),
            "furtherQuestions": decrypted_feedback.get("furtherQuestions"), "comment": decrypted_feedback.get("comment"),
            "highlights": []
        })

        if cached_units_data:
            for unit_data in cached_units_data:
                assessments = unit_data.get('assessments')
                if assessments:
                    for assessment in assessments:
                        if assessment['id'] == feedback.assessmentId:
                            feedbacks_dict[feedback.id]['unitCode'] = unit_data['id']
                            feedbacks_dict[feedback.id]['year'] = unit_data['year']
                            feedbacks_dict[feedback.id]['semester'] = unit_data['semester']
                            feedbacks_dict[feedback.id]['assessmentName'] = assessment['assessmentName']

                            break

        if highlight:
            start_meta = highlight.startMeta
            end_meta = highlight.endMeta

            parsed_start_meta = json.loads(start_meta) if start_meta is not None else DomMeta(parentTagName="div",
                                                                                              parentIndex=0,
                                                                                              textOffset=0)
            parsed_end_meta = json.loads(end_meta) if end_meta is not None else DomMeta(parentTagName="div",
                                                                                        parentIndex=0, textOffset=0)
            highlight_data = HighlightPydantic(
                id=highlight.id, startMeta=parsed_start_meta,
                endMeta=parsed_end_meta, text=highlight.text,
                annotationTag=highlight.annotationTag, notes=highlight.notes,
                feedbackId=highlight.feedbackId,
                commonTheme=highlight.commonTheme
            )
            filtered_action_items = json.loads(actionItems)
            complete_highlight = {
                'annotation': highlight_data,
                'actionItems':  [value for value in filtered_action_items if value["action"] != None ]
            }
            feedback_entry['highlights'].append(complete_highlight)
    feedbacks_list = list(feedbacks_dict.values())
    return feedbacks_list


def get_feeedbacks_by_unitcode_assessment(unit_code, assessment_name, db: Session):
    # Trim whitespace from input parameters
    unit_code = unit_code.strip() if unit_code else unit_code
    assessment_name = assessment_name.strip() if assessment_name else assessment_name

    query = (
        db.query(Feedback, Assessment, Highlight, func.concat('[', func.group_concat(
            func.json_object(
                'id', AnnotationActionPoint.id,
                'action', AnnotationActionPoint.action,
                'category', AnnotationActionPoint.category,
                'deadline', AnnotationActionPoint.deadline,
                'status', AnnotationActionPoint.status
            )
        ), ']').label('actionItems'))
        .join(Assessment, Feedback.assessmentId == Assessment.id)
        .outerjoin(Highlight, (Feedback.id == Highlight.feedbackId) & (Highlight.rowStatus == "ACTIVE"))
        .outerjoin(AnnotationActionPoint, (Highlight.id == AnnotationActionPoint.highlightId) & 
                   (AnnotationActionPoint.rowStatus == "ACTIVE"))
        .filter(
            func.trim(Assessment.unitId) == unit_code,
            func.trim(Assessment.assessmentName) == assessment_name,
            Feedback.rowStatus == "ACTIVE"
        )
        .group_by(Feedback.id, Highlight.id)
    )

    result = query.all()
    feedbacks_dict = {}
    
    if len(result) == 0:
        return None

    for row in result:
        feedback, assessment, highlight, actionItems = row
        
        # Decrypt feedback data
        decrypted_feedback = _decrypt_feedback_emails(feedback)
        
        feedback_entry = feedbacks_dict.setdefault(feedback.id, {
            "id": decrypted_feedback["id"],
            "url": decrypted_feedback["url"],
            "assessmentId": decrypted_feedback["assessmentId"],
            "studentEmail": decrypted_feedback["studentEmail"],
            "mark": decrypted_feedback["mark"],
            "performance": decrypted_feedback.get("performance"),
            "clarity": decrypted_feedback.get("clarity"),
            "evaluativeJudgement": decrypted_feedback.get("evaluativeJudgement"),
            "personalise": decrypted_feedback.get("personalise"),
            "usability": decrypted_feedback.get("usability"),
            "emotion": decrypted_feedback.get("emotion"),
            "furtherQuestions": decrypted_feedback.get("furtherQuestions"),
            "comment": decrypted_feedback.get("comment"),
            "highlights": []
        })

        if highlight:
            start_meta = highlight.startMeta
            end_meta = highlight.endMeta

            parsed_start_meta = json.loads(start_meta) if start_meta is not None else DomMeta(parentTagName="div",
                                                                                              parentIndex=0,
                                                                                              textOffset=0)
            parsed_end_meta = json.loads(end_meta) if end_meta is not None else DomMeta(parentTagName="div",
                                                                                        parentIndex=0, textOffset=0)
            highlight_data = HighlightPydantic(
                id=highlight.id,
                startMeta=parsed_start_meta,
                endMeta=parsed_end_meta,
                text=highlight.text,
                annotationTag=highlight.annotationTag,
                notes=highlight.notes,
                feedbackId=highlight.feedbackId,
                commonTheme=highlight.commonTheme
            )
            filtered_action_items = json.loads(actionItems)
            complete_highlight = {
                'annotation': highlight_data,
                'actionItems': [value for value in filtered_action_items if value["action"] != None]
            }
            feedback_entry['highlights'].append(complete_highlight)

    feedbacks_list = list(feedbacks_dict.values())
    return feedbacks_list