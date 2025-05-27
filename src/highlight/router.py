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
    result = service.create_highlight(db, highlight, user['email'])
    if result is None:
        raise HTTPException(status_code=403, detail="You can only create highlights on your own feedback")
    return {"message": "Highlight created successfully"}



@router.get("/all", response_model=List[HighlightPydantic])
def get_highlights(db: Session = Depends(get_db)):
    return service.get_highlights(db)


@router.get("/tags", response_model=List[str])
def get_highlight_tags(db: Session = Depends(get_db)):
    return service.get_highlight_tags(db)

@router.patch("/{highlight_id}/notes")
def update_highlight_notes_route(highlight_id,notes:str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    highlight = service.update_highlight_notes(db, highlight_id, notes, user['email'])
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found or you don't have permission to modify it")
    return highlight

@router.delete("/{highlight_id}", response_model=bool)
def delete_highlight(highlight_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    result = service.delete_highlight(db, highlight_id, user['email'])
    if not result:
        raise HTTPException(status_code=404, detail="Highlight not found or you don't have permission to delete it")
    return result

