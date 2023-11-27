from sqlalchemy import Column, String, Integer, Enum, Table
from .enums import Role
from src.database import engine
from src.base import get_base

Base = get_base()


class User(Base):
    __table__ = Table("USER", Base.metadata, autoload_with=engine)

# monashId refers to student or staff ID number
# monashObjectId is something that can be used as a unique identifier and anchor in the monash system
