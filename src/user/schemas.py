from typing import Optional

from pydantic import BaseModel

from .enums import Role, Faculty


class UserPydantic(BaseModel):
    monashId: str
    monashObjectId: Optional[str] = None
    authcate: str
    email: str
    lastName: str
    firstName: str
    role: Role
    password: Optional[str]= None
    faculty: Faculty

