from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.annotation import service
from src.action.schemas import ActionPydantic
from src.login.service import get_current_user
from src.action.service import add_action_point_to_highlight

router = APIRouter()

@router.post("/{highlight_id}/action")
def add_action_point_to_highlight_route(highlight_id, action_point:ActionPydantic, db: Session = Depends(get_db), user=Depends(get_current_user)):

    return add_action_point_to_highlight(highlight_id, action_point, db)