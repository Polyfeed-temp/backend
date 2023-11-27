from sqlalchemy import Table

from src.base import get_base
from src.database import engine

Base = get_base()


class AnnotationActionPoint(Base):
    __table__ = Table("ACTION", Base.metadata, autoload_with=engine)
