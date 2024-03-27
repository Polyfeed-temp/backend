from typing import List
from .schemas import AssessmentPydantic
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.assessment import service

router = APIRouter()


@router.get("/all", response_model=List[AssessmentPydantic])
def get_assessments(db: Session = Depends(get_db)):
    return service.get_all_assessments(db)


@router.post("/", response_model=AssessmentPydantic)
def create_assessment(assessment: AssessmentPydantic, db: Session = Depends(get_db)):
    return service.create_assessment(db, assessment)


@router.get("/{assessmentId}", response_model=AssessmentPydantic)
def get_assessment_by_id(assessmentId: int, db: Session = Depends(get_db)):
    return service.get_assessment_by_id(db, assessmentId)


@router.patch("/{assessmentId}", response_model=AssessmentPydantic)
def update_assessment_by_id(assessmentId: int, assessment: AssessmentPydantic, db: Session = Depends(get_db)):
    return service.update_assessment(db, assessmentId, assessment)


@router.delete("/{assessmentId}", response_model=bool)
def delete_assessment_by_id(assessmentId: int, db: Session = Depends(get_db)):
    return service.delete_assessment(db, assessmentId)


@router.get("/unit/{unitCode}", response_model=List[AssessmentPydantic])
def get_assessment_by_unitcode(unitCode: str, db: Session = Depends(get_db)):
    return service.get_assessments_by_unit(db, unitCode)
