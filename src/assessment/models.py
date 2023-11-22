from sqlalchemy import Column, String, Integer, ForeignKey
from src.base import get_base
from sqlalchemy.orm import relationship

Base = get_base()

class Assessment(Base):
    __tablename__ = 'ASSESSMENT'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unitCode = Column(String(10), ForeignKey('UNIT.unitCode'))
    assessmentName = Column(String(255))

# may need to change studentId to User.monashId
