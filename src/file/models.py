from sqlalchemy import Table
from datetime import datetime
from src.base import get_base
from src.database import engine

Base = get_base()
class File(Base):
    __table__ = Table("File", Base.metadata, autoload_with=engine)