from sqlalchemy import Column, String, Integer, ForeignKey, Date, Enum, JSON, UUID, BINARY, Table
from sqlalchemy.orm import relationship
from .enums import AnnotationTag, ActionPointCategory
import uuid
from src.base import get_base
from src.database import engine
Base = get_base()

class Highlight(Base):
    __table__ = Table("HIGHLIGHT",Base.metadata, autoload_with=engine)

class AnnotationActionPoint(Base):
    __table__ = Table("ACTION",Base.metadata, autoload_with=engine)

