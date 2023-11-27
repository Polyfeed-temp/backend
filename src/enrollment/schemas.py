from pydantic import BaseModel


class EnrollmentPydantic(BaseModel):
    id: int
    userEmail: str
    unitCode: str
