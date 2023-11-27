from sqlalchemy import Table

from src.base import get_base
from src.database import engine

Base = get_base()


class Feedback(Base):
    __table__ = Table("FEEDBACK", Base.metadata, autoload_with=engine)
