from typing import List
from .schemas import HighlightPydantic
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.annotation import service

router = APIRouter()


@router.get("/", response_model=List[HighlightPydantic])
def get_highlights_url(url: str, db: Session = Depends(get_db)):
    return service.get_highlights_by_url(db, url)


@router.post("/", response_model=HighlightPydantic)
def create_highlight(highlight: HighlightPydantic, db: Session = Depends(get_db)):
    print(highlight)
    return service.create_highlight(db, highlight)


@router.get("/all", response_model=List[HighlightPydantic])
def get_highlights(db: Session = Depends(get_db)):
    return service.get_highlights(db)


@router.get("/tags", response_model=List[str])
def get_highlight_tags(db: Session = Depends(get_db)):
    return service.get_highlight_tags(db)
