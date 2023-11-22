from sqlalchemy import Column, String, Integer, ForeignKey, Date, Enum, JSON, UUID, BINARY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .enums import AnnotationTag, ActionPointCategory
from sqlalchemy.dialects.mysql import BINARY
import uuid

Base = declarative_base()
class Highlight(Base):
    __tablename__ = 'HIGHLIGHTS'
    id = Column(String(36), primary_key=True)
    startMeta = Column(JSON)
    endMeta = Column(JSON)
    text = Column(String(255))
    url = Column(String(255))
    annotationTag = Column(Enum(AnnotationTag))
    notes = Column(String(255))
    unit = Column(String(10), ForeignKey('UNITS.unitCode'))

class AnnotationActionPoint(Base):
    __tablename__ = 'ACTIONS'
    id = Column(Integer, primary_key=True)
    action = Column(String(255))
    actionPoint = Column(Enum(ActionPointCategory))
    deadline = Column(Date)
    annotationId = Column(String(255), ForeignKey('HIGHLIGHTS.id'))

class Unit(Base):
    __tablename__ = 'UNITS'
    unitCode = Column(String(10), primary_key=True)
