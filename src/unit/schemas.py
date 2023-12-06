from pydantic import BaseModel
from typing import Optional, List
from src.assessment.schemas import AssessmentPydantic


class UnitPydantic(BaseModel):
    unitId: str
    unitCode: str
    unitName: str
    year:str
    semester:str

# class UnitWithAssessmentPydantic(UnitPydantic):
#     assessment = List[AssessmentPydantic]
