from sqlalchemy import Table, Column, Integer, String, JSON, MetaData
from src.base import get_base
from src.database import engine
import json
from .schemas import RubricItem

Base = get_base()
metadata = MetaData()

class FeedbackRequest(Base):
    __table__ = Table("FEEDBACK_REQUEST", Base.metadata, autoload_with=engine)

    def get_rubric_items(self):
        """Convert JSON string to RubricItem objects"""
        if isinstance(self.rubricItems, str):
            items_list = json.loads(self.rubricItems)
            return [RubricItem(**item) for item in items_list]
        return self.rubricItems