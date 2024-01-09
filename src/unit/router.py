from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.unit.service import get_all_units_with_assessments

router = APIRouter()


# @router.get("/all", response_model=List[UnitPydantic])
# def get_units(db: Session = Depends(get_db)):
#     return service.get_units(db)
#
#
# @router.post("/", response_model=UnitPydantic)
# def create_unit(unit: UnitPydantic, db: Session = Depends(get_db)):
#     print(unit)
#     return service.create_unit(db, unit)
#
#
# @router.get("/{unitCode}", response_model=UnitPydantic)
# def get_unit_by_id(unitCode: str, db: Session = Depends(get_db)):
#     return service.get_unit_by_id(db, unitCode)
#
#
# @router.patch("/{unitCode}", response_model=UnitPydantic)
# def update_unit_by_code(unitCode: str, unit: UnitPydantic, db: Session = Depends(get_db)):
#     return service.update_unit(db, unit, unitCode)
#
#
# @router.delete("/{unitCode}", response_model=bool)
# def delete_unit_by_code(unitCode: str, db: Session = Depends(get_db)):
#     return service.delete_unit(db, unitCode)

@router.get("/all")
def get_all_units_with_assessments_route(db: Session = Depends(get_db)):
    return get_all_units_with_assessments(db)