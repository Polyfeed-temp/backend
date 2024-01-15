from sqlalchemy.orm import Session
from src.action.models import AnnotationActionPoint
import json
def add_action_point_to_highlight(highlight_id, action_point, db: Session):
    db_action = AnnotationActionPoint(action=action_point.action, category=action_point.category.value, deadline=action_point.deadline, highlightId=str(highlight_id) )
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action

