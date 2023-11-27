from sqlalchemy import Column, String, Integer, Table
from src.database import engine
from src.base import get_base

Base = get_base()

class Unit(Base):
    __table__ = Table("UNIT", Base.metadata, autoload_with=engine)

# offering example: S2 2023
