from pydantic import BaseModel


class AssessmentPydantic(BaseModel):
    id: int
    unitCode: str
    assessmentName: str
