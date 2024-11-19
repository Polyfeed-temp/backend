from sqlalchemy.orm import Session
from . import models
from . import schemas

def create_file(db: Session, file: schemas.FileCreate):
    db_file = models.File(
        feedback_id=file.feedback_id,
        file_content=file.file_content
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_files_by_feedback_id(db: Session, feedback_id: int):
    return db.query(models.File).filter(models.File.feedback_id == feedback_id).all()
