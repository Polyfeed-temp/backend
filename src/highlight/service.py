import json

from sqlalchemy.orm import Session

from .models import Highlight
from .schemas import DomMeta, CompleteHighlight
from src.action.models import AnnotationActionPoint
from src.feedback.models import Feedback
from src.user.encryption import decrypt_field


localDatabase = []


def _verify_feedback_ownership(db: Session, feedback_id: int, user_email: str) -> bool:
    """Verify that the user owns the feedback by checking encrypted email."""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        return False
    
    try:
        decrypted_email = decrypt_field(feedback.studentEmail)
        return decrypted_email == user_email
    except:
        # If decryption fails, check if it's already unencrypted
        return feedback.studentEmail == user_email


def _verify_highlight_ownership(db: Session, highlight_id: str, user_email: str) -> bool:
    """Verify that the user owns the highlight by checking the associated feedback."""
    highlight = db.query(Highlight).filter(Highlight.id == highlight_id).first()
    if not highlight:
        return False
    
    return _verify_feedback_ownership(db, highlight.feedbackId, user_email)


def get_highlights_by_url(db: Session, url: str):
    db_highlights = db.query(Highlight).filter(Highlight.url == url, Highlight.rowStatus == "ACTIVE").all()
    if db_highlights:
        for db_highlight in db_highlights:
            db_highlight.start_meta = DomMeta(**json.loads(db_highlight.start_meta))
            db_highlight.end_meta = DomMeta(**json.loads(db_highlight.end_meta))
    return db_highlights


def create_highlight(db: Session, highlight_data: CompleteHighlight, user_email: str = None):
    """Create a highlight with optional user verification."""
    highlight = highlight_data.annotation
    
    # Verify feedback ownership if user_email is provided
    if user_email and not _verify_feedback_ownership(db, highlight.feedbackId, user_email):
        return None
    
    start_meta = (highlight.startMeta.model_dump_json())
    end_meta = highlight.endMeta.model_dump_json()

    db_highlight = Highlight(id=str(highlight.id), startMeta=start_meta,
                             endMeta=end_meta, text=highlight.text, annotationTag=highlight.annotationTag.value,
                             notes=highlight.notes, feedbackId=str(highlight.feedbackId),gptResponse=highlight.gptResponse)

    db.add(db_highlight)
    db.commit()

    if highlight_data.actionItems:
        for action in highlight_data.actionItems:
            db_action= AnnotationActionPoint(action=action.action, 
                                             category=action.category.value, 
                                             deadline=action.deadline, 
                                             highlightId=str(highlight.id),
                                             rowStatus="ACTIVE")
            db.add(db_action)

    db.commit()
    db.refresh(db_highlight)
    return db_highlight


def update_highlight_notes(db: Session, id: str, notes: str, user_email: str = None):
    """Update highlight notes with optional user verification."""
    # Verify ownership if user_email is provided
    if user_email and not _verify_highlight_ownership(db, id, user_email):
        return None
    
    db_highlight = db.query(Highlight).filter(Highlight.id == id).first()
    if db_highlight:
        db_highlight.notes = notes
        db.commit()
        db.refresh(db_highlight)
        return db_highlight
    return None


def delete_highlight(db: Session, highlight_id: str, user_email: str = None):
    """Delete a highlight with optional user verification."""
    # Verify ownership if user_email is provided
    if user_email and not _verify_highlight_ownership(db, highlight_id, user_email):
        return False
    
    db_highlight = db.query(Highlight).filter(Highlight.id == highlight_id).first()
    if db_highlight:
        db_highlight.rowStatus = "INACTIVE"
        db.commit()
        return True
    return False


def get_highlights(db: Session):
    return db.query(Highlight).all()


def get_highlight_tags(db: Session):
    return db.query(Highlight.annotation_tag).distinct().all()
