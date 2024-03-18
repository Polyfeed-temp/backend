from sqlalchemy import Table

from src.base import get_base
from src.database import engine

Base = get_base()


class Log(Base):
    __table__ = Table("LOG", Base.metadata, autoload_with=engine)
