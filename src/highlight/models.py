from sqlalchemy import Table

from src.base import get_base
from src.database import engine

Base = get_base()


class Highlight(Base):
    __table__ = Table("HIGHLIGHT", Base.metadata, autoload_with=engine)
