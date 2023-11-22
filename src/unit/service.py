from sqlalchemy.orm import Session
from .models import Unit
from .schemas import UnitPydantic
import json


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
