from typing import List
from .schemas import EnrollmentPydantic
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.enrollment import service

router = APIRouter()


@router.get("/all", response_model=List[EnrollmentPydantic])
def get_all_student_units(db: Session = Depends(get_db)):
    return service.get_all_student_units(db)


@router.post("/", response_model=EnrollmentPydantic)
def create_student_unit(student_unit: EnrollmentPydantic, db: Session = Depends(get_db)):
    return service.create_student_unit(db, student_unit)


@router.get("/{studentUnitId}", response_model=EnrollmentPydantic)
def get_student_unit_by_id(studentUnitId: int, db: Session = Depends(get_db)):
    return service.get_student_unit_by_id(db, studentUnitId)


@router.patch("/{studentUnitId}", response_model=EnrollmentPydantic)
def update_student_unit_by_id(studentUnitId: int, student_unit: EnrollmentPydantic, db: Session = Depends(get_db)):
    return service.update_student_unit(db, studentUnitId, student_unit)


@router.delete("/{studentUnitId}", response_model=bool)
def delete_student_unit_by_id(studentUnitId: int, db: Session = Depends(get_db)):
    return service.delete_student_unit(db, studentUnitId)


@router.get("/student/{studentId}", response_model=List[EnrollmentPydantic])
def get_student_all_units(studentId: int, db: Session = Depends(get_db)):
    return service.get_student_all_units(db, studentId)

@router.get("/unit/{unitCode}/students", response_model=List[EnrollmentPydantic])
def get_students_by_unit(unitCode: str, db: Session = Depends(get_db)):
    return service.get_students_by_unit(db, unitCode)