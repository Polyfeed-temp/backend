from typing import Optional, List

from pydantic import BaseModel

from .enums import Role, Faculty


class UserPydantic(BaseModel):
    monashId: Optional[str] =None
    monashObjectId: Optional[str] = None
    authcate: str
    email: str
    lastName: str
    firstName: str
    role: Role
    password: Optional[str]= None
    faculty: Faculty

class UserSignupRequest(BaseModel):
    email: str
    password: str
    firstName: str
    lastName: str
    monashId: Optional[str] = None

class AssessmentPydantic(BaseModel):
    id: int
    assessmentName: str
class EnrolledUnitPydantic(BaseModel):
    unitCode: str
    assessments: List[AssessmentPydantic]
