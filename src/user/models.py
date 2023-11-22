from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'USER'
    id = Column(Integer, primary_key=True, autoincrement=True)
    monash_id = Column(String(255))
    monash_object_id = Column(String(255))
    authcate = Column(String(255))
    email = Column(String(255))
    last_name = Column(String(255))
    first_name = Column(String(255))
