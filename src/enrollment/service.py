from sqlalchemy.orm import Session
from .models import Enrollment
from .schemas import EnrollmentPydantic


# Function to create a student unit
def create_student_unit(db: Session, student_unit: EnrollmentPydantic):
    db_student_unit = Enrollment(**student_unit.model_dump())
    db.add(db_student_unit)
    db.commit()
    db.refresh(db_student_unit)
    return db_student_unit


# Function to read a student unit by ID
def get_student_unit_by_id(db: Session, student_unit_id: int):
    return db.query(Enrollment).filter(Enrollment.id == student_unit_id).first()


# Function to get all student units
def get_all_student_units(db: Session):
    return db.query(Enrollment).all()


# Function to update a student unit
def update_student_unit(db: Session, student_unit_id: int, updated_student_unit: EnrollmentPydantic):
    db.query(Enrollment).filter(Enrollment.id == student_unit_id).update(updated_student_unit.dict())
    db.commit()
    return updated_student_unit


# Function to delete a student unit
def delete_student_unit(db: Session, student_unit_id: int):
    student_unit = db.query(Enrollment).filter(Enrollment.id == student_unit_id).first()
    if student_unit:
        db.delete(student_unit)
        db.commit()
        return True
    else:
        return False


def get_student_all_units(db: Session, studentId: int):
    return db.query(Enrollment).filter(Enrollment.studentId == studentId).all()


def get_students_by_unit(db: Session, unitCode: str):
    return db.query(Enrollment).filter(Enrollment.unitCode == unitCode).all()
