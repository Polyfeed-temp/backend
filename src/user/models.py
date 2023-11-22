from sqlalchemy import Column, String, Integer, Enum
from .enums import Role
from src.base import get_base

Base = get_base()


class User(Base):
    __tablename__ = 'USER'
    id = Column(Integer, primary_key=True, autoincrement=True)
    monashId = Column(String(10))
    monashObjectId = Column(String(255))
    authcate = Column(String(255))
    email = Column(String(255))
    lastName = Column(String(255))
    firstName = Column(String(255))
    role = Column(Enum(Role))

# monashId refers to student or staff ID number
# monashObjectId is something that can be used as a unique identifier and anchor in the monash system
