from sqlalchemy import Column, String, Integer
from src.base import get_base

Base = get_base()

class Unit(Base):
    __tablename__ = 'UNIT'
    unitCode = Column(String(10), primary_key=True)
    unitName = Column(String(255))
    offering = Column(String(255))

# offering example: S2 2023
