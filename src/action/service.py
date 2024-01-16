from sqlalchemy.orm import Session
from src.action.models import AnnotationActionPoint
from src.action.schemas import ActionPydantic
from typing import List
import json
def add_action_point_to_highlight(highlight_id, action_point, db: Session):
    db_action = AnnotationActionPoint(action=action_point.action, category=action_point.category.value, deadline=action_point.deadline, highlightId=str(highlight_id) )
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action

def update_action_points(highlight_id, action_points: List[ActionPydantic], db: Session):
    # Query the existing action points
    existing_action_points = db.query(AnnotationActionPoint).filter(AnnotationActionPoint.highlightId == str(highlight_id)).all()

    # Delete existing action points
    for action_point in existing_action_points:
        db.delete(action_point)

    # Add new action points
    for action_point in action_points:
        db_action = AnnotationActionPoint(
            action=action_point.action,
            category=action_point.category.value,
            deadline=action_point.deadline,
            highlightId=str(highlight_id),
            status=action_point.completed or False
        )
        db.add(db_action)

    # Commit the transaction
    db.commit()
    return True
