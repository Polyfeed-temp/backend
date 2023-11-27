from sqlalchemy import Table

from src.base import get_base
from src.database import engine

Base = get_base()


class Enrollment(Base):
    __table__ = Table("ENROLLMENT", Base.metadata, autoload_with=engine)

# may need to change studentId to User.monashId
