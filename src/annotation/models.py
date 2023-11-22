from sqlalchemy import Column, String, Integer, ForeignKey, Date, Enum, JSON, UUID, BINARY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .enums import AnnotationTag, ActionPointCategory
from src.unit.models import Unit
from sqlalchemy.dialects.mysql import BINARY
import uuid

Base = declarative_base()
class Highlight(Base):
    __tablename__ = 'HIGHLIGHT'
    id = Column(String(36), primary_key=True)
    startMeta = Column(JSON)
    endMeta = Column(JSON)
    text = Column(String(255))
    url = Column(String(255))
    annotationTag = Column(Enum(AnnotationTag))
    notes = Column(String(255))
    unitCode = Column(String(10), ForeignKey('src.unit.models.UNIT.unitCode'))
    unit = relationship("src.unit.models.Unit")

class AnnotationActionPoint(Base):
    __tablename__ = 'ACTION'
    id = Column(Integer, primary_key=True)
    action = Column(String(255))
    actionPoint = Column(Enum(ActionPointCategory))
    deadline = Column(Date)
    annotationId = Column(String(255), ForeignKey('HIGHLIGHT.id'))

