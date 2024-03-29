from sqlalchemy import Table

from src.base import get_base
from src.database import engine

Base = get_base()

class Unit(Base):
    __table__ = Table("UNIT", Base.metadata, autoload_with=engine)

# offering example: S2 2023
