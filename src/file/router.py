from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import service
from .schemas import File, FileCreate

router = APIRouter()

@router.post("/", response_model=File)
def create_file(file: FileCreate, db: Session = Depends(get_db)):
    return service.create_file(db, file)

@router.get("/list/{feedback_id}", response_model=list[File])
def get_files_by_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    files = service.get_files_by_feedback_id(db, feedback_id)
    if not files:
        raise HTTPException(status_code=404, detail="No files found for this feedback")
    return files

