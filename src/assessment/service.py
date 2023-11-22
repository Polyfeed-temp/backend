from sqlalchemy.orm import Session
from .models import Assessment
from .schemas import AssessmentPydantic

# Function to create an assessment
def create_assessment(db: Session, assessment: AssessmentPydantic):
    db_assessment = Assessment(**assessment.model_dump())
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

# Function to read an assessment
def get_assessment_by_id(db: Session, assessment_id: int):
    return db.query(Assessment).filter(Assessment.id == assessment_id).first()

def get_all_assessments(db: Session):
    return db.query(Assessment).all()

def get_assessments_by_unit(db: Session, unitCode: str):
    return db.query(Assessment).filter(Assessment.unitCode == unitCode).all()

# Function to update an assessment
def update_assessment(db: Session, assessment_id: int, updated_assessment: AssessmentPydantic):
    db.query(Assessment).filter(Assessment.id == assessment_id).update(updated_assessment.dict())
    db.commit()
    return updated_assessment

# Function to delete an assessment
def delete_assessment(db: Session, assessment_id: int):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).all()
    if len(assessment) == 1:
        db.delete(assessment)
        db.commit()
        return True
    else:
        return False

