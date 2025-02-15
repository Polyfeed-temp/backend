from typing import Optional, List
from pydantic import BaseModel, field_validator
import json

class RubricItem(BaseModel):
    item: str
    comments: str

class FeedbackRequestPydantic(BaseModel):
    id: Optional[int] = None
    assignmentId: int
    rubricItems: List[RubricItem]
    student_id: Optional[str] = None
    AI_RubricItem: Optional[str] = None

    @field_validator('rubricItems', mode='before')
    @classmethod
    def parse_rubric_items(cls, value):
        if isinstance(value, str):
            items = json.loads(value)
            return [RubricItem(**item) for item in items]
        return value

    class Config:
        from_attributes = True