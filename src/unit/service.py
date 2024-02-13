from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Unit
from src.assessment.models import Assessment
from .schemas import UnitPydantic
import json
from src.database import unit as cached_units_data


def get_unit_by_id(db: Session, unitCode: str):
    db_unit = db.query(Unit).filter(Unit.unitCode == unitCode).all()
    if len(db_unit) == 1:
        return db_unit
    else:
        return "Error: More than one unit / No Unit found with the unit code."


def create_unit(db: Session, unitData: UnitPydantic):
    db_unit = Unit(**unitData.model_dump())
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit


def get_units(db: Session):
    return db.query(Unit).all()


def update_unit(db: Session, unitData: UnitPydantic, unitCode: str):
    db_unit = db.query(Unit).filter(Unit.unitCode == unitCode).all()
    if len(db_unit) == 1:
        for field, value in unitData.model_dump().items():
            setattr(db_unit, field, value)

        db.commit()
        db.refresh(db_unit)
        return db_unit
    else:
        return "Error: More than one user / No User found with the ID."


def delete_unit(db: Session, unitCode: str):
    db_unit = db.query(Unit).filter(Unit.unitCode == unitCode).all()
    if len(db_unit) == 1:
        db.delete(db_unit)
        db.commit()
        return True
    else:
        return False
def get_all_units_with_assessments(db: Session):
    # global cached_units_data
    if cached_units_data.get_data():
        return cached_units_data.get_data()
    subquery = (
        db.query(func.concat('[', func.group_concat(
            func.json_object('assessmentName', Assessment.assessmentName, 'id', Assessment.id)
        ), ']'))
        .filter(Unit.unitId == Assessment.unitId)
        .correlate(Unit)
        .as_scalar()
    )

    query = (
        db.query(
            func.json_object('id', Unit.unitId, 'unitCode', Unit.unitCode, 'year', Unit.year, 'semester', Unit.semester).label('Unit'),
            subquery.label('concatenated_assessments')
        )
        .group_by(Unit.unitId)
    )

    result = query.all()
    all_units=[]
    # Process the result as needed
    for unit_data in result:
        unit, assessments = unit_data
        unit_dict =json.loads(unit)
        if assessments:
            unit_dict['assessments'] = json.loads(assessments)
            print(unit_dict)
        all_units.append(unit_dict)

    cached_units_data.insert_data(all_units)
    return all_units
