from sqlalchemy import Column, String, Integer, ForeignKey, Table
from src.database import engine
from src.base import get_base
from sqlalchemy.orm import relationship

Base = get_base()

class Assessment(Base):
    __table__ = Table("ASSESSMENT", Base.metadata, autoload_with=engine)

# may need to change studentId to User.monashId
