from typing import List

from pydantic import UUID4

from .schemas import HighlightPydantic
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.highlight import service
from src.login.service import get_current_user
from src.highlight.schemas import CompleteHighlight

router = APIRouter()




@router.post("/")
def create_highlight(highlight: CompleteHighlight, db: Session = Depends(get_db), user=Depends(get_current_user)):
    email = user.email
    #check if feedback user match email
    service.create_highlight(db, highlight)



@router.get("/all", response_model=List[HighlightPydantic])
def get_highlights(db: Session = Depends(get_db)):
    return service.get_highlights(db)


@router.get("/tags", response_model=List[str])
def get_highlight_tags(db: Session = Depends(get_db)):
    return service.get_highlight_tags(db)
@router.patch("/{highlight_id}/notes")
def update_highlight_notes_route(highlight_id,notes:str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    highligh =service.update_highlight_notes(db, highlight_id, notes)
    if not highligh:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return highligh
@router.delete("/{highlight_id}", response_model=bool)
def delete_highlight(highlight_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return service.delete_highlight(db, highlight_id)

