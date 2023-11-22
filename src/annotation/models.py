from sqlalchemy import Column, String, Integer, ForeignKey, Date, Enum, JSON, UUID, BINARY
from sqlalchemy.orm import relationship
from .enums import AnnotationTag, ActionPointCategory
import uuid
from src.base import get_base

Base = get_base()

class Highlight(Base):
    __tablename__ = 'HIGHLIGHT'
    id = Column(String(36), primary_key=True)
    startMeta = Column(JSON)
    endMeta = Column(JSON)
    text = Column(String(255))
    url = Column(String(255))
    annotationTag = Column(Enum(AnnotationTag))
    notes = Column(String(255))
    unitCode = Column(String(10), ForeignKey('UNIT.unitCode'))
    unit = relationship("Unit")
    studentId = Column(Integer, ForeignKey('USER.id'))

class AnnotationActionPoint(Base):
    __tablename__ = 'ACTION'
    id = Column(Integer, primary_key=True)
    action = Column(String(255))
    actionPoint = Column(Enum(ActionPointCategory))
    deadline = Column(Date)
    annotationId = Column(String(255), ForeignKey('HIGHLIGHT.id'))

