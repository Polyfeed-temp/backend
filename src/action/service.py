from sqlalchemy.orm import Session
from src.action.models import AnnotationActionPoint
from src.action.schemas import ActionPydantic
from typing import List
def add_action_point_to_highlight(highlight_id, action_point, db: Session):
    db_action = AnnotationActionPoint(action=action_point.action, category=action_point.category.value, deadline=action_point.deadline, highlightId=str(highlight_id) )
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action

def update_action_points(highlight_id, action_points: List[ActionPydantic], db: Session):
    # Query the existing action points

    # Add new action points
    for action_point in action_points:

        if action_point.id:
            db_action = db.query(AnnotationActionPoint).filter(AnnotationActionPoint.id == action_point.id).first()

            if not db_action:
                continue;

            db_action.deadline=action_point.deadline
            db_action.status=action_point.status or False
        else:
            db_action = AnnotationActionPoint(
                action=action_point.action,
                category=action_point.category.value,
                deadline=action_point.deadline,
                highlightId=str(highlight_id),
                status=action_point.status or False
            )
            db.add(db_action)

    # Commit the transaction
    db.commit()
    return True

def update_action_status(action_id, status, db):
    db_action = db.query(AnnotationActionPoint).filter(AnnotationActionPoint.id == action_id).first()
    if not db_action:
        return False
    
    db_action.status = 1 if status else 0
    db.commit()
    return True

def delete_action_point(action_id, db):
    db_action = db.query(AnnotationActionPoint).filter(AnnotationActionPoint.id == action_id).first()
    if not db_action:
        return False
    # db.delete(db_action)

    db_action.rowStatus = "INACTIVE"
    db.commit()
    return True