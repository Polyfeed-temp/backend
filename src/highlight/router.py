from typing import List
from .schemas import HighlightPydantic
from fastapi import APIRouter, Depends
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
@router.delete("/{highlight_id}", response_model=bool)
def delete_highlight(highlight_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return service.delete_highlight(db, highlight_id)
