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
    start_meta = Column(JSON)
    end_meta = Column(JSON)
    text = Column(String(255))
    url = Column(String(255))
    annotation_tag = Column(Enum(AnnotationTag))
    notes = Column(String(255))

class AnnotationActionPoint(Base):
    __tablename__ = 'ACTIONS'
    id = Column(Integer, primary_key=True)
    action = Column(String(255))
    actionpoint = Column(Enum(ActionPointCategory))
    deadline = Column(Date)
    annotation_id = Column(String(255), ForeignKey('HIGHLIGHTS.id'))

