from pydantic import BaseModel
from typing import Optional


class AssessmentPydantic(BaseModel):
    id: int
    unitId: Optional[str] = None
    assessmentName: str
