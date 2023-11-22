from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.ext.declarative import declarative_base
from .enums import Role

Base = declarative_base()


class User(Base):
    __tablename__ = 'USER'
    id = Column(Integer, primary_key=True, autoincrement=True)
    monashId = Column(String(255))
    monashObjectId = Column(String(255))
    authcate = Column(String(255))
    email = Column(String(255))
    lastName = Column(String(255))
    firstName = Column(String(255))
    role = Column(Enum(Role))
