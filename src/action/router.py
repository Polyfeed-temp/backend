from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.annotation import service
from src.action.schemas import ActionPydantic
from src.login.service import get_current_user
from src.action.service import add_action_point_to_highlight, update_action_points, update_action_status, delete_action_point

router = APIRouter()

@router.post("/{highlight_id}/action")
def add_action_point_to_highlight_route(highlight_id, action_point:ActionPydantic, db: Session = Depends(get_db), user=Depends(get_current_user)):

    return add_action_point_to_highlight(highlight_id, action_point, db)

@router.patch("/{highlight_id}/action")
def update_action_points_route(highlight_id:str, action_point: List[ActionPydantic], db: Session = Depends(get_db), user=Depends(get_current_user)):

    return update_action_points(highlight_id, action_point, db)
@router.patch("/{action_id}/status")
def update_action_status_route(action_id:str, status:bool, db: Session = Depends(get_db), user=Depends(get_current_user)):
    status= update_action_status(action_id, status, db)
    if not status:
        raise HTTPException(status_code=404, detail="Action not found")
    return status

@router.delete("/{action_id}")
def delete_action_point_route(action_id, db: Session = Depends(get_db)):
    status= delete_action_point(action_id, db)
    if not status:
        raise HTTPException(status_code=404, detail="Action not found")
    return status

