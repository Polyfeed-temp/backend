from sqlalchemy import Column, String, Integer, ForeignKey
from src.base import get_base
from sqlalchemy.orm import relationship

Base = get_base()

class StudentUnit(Base):
    __tablename__ = 'STUDENT_UNIT'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unitCode = Column(String(10), ForeignKey('UNIT.unitCode'))
    studentId = Column(Integer, ForeignKey('USER.id'))

# may need to change studentId to User.monashId
