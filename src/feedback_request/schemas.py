from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class RubricItem(BaseModel):
    id: UUID
    item: str
    comments: str

class FeedbackRequestCreate(BaseModel):
    assignmentId: int
    rubricItems: List[RubricItem]
    previousFeedbackUsage: str

class FeedbackRequestResponse(FeedbackRequestCreate):
    id: int
    aiRubricItems: Optional[List[RubricItem]] = None
    AI_RubricItem: Optional[str] = None
    AI_FBRequest: Optional[str] = None 