from pydantic import BaseModel
from typing import Optional, List
from pydantic import HttpUrl
from src.highlight.schemas import CompleteHighlight


class FeedbackBasePydantic(BaseModel):
    id: Optional[int] = None
    mark: float
    totalMark: int
    clarity: Optional[int] = None
    personalise: Optional[int] = None
    usability: Optional[int] = None
    emotion: Optional[int] = None
    furtherQuestions: Optional[str] = None
    comment: Optional[str] = None
    markerEmail: Optional[str] = None
    studentEmail: str
    assessmentId: int
    performance: Optional[int] = None
    feedbackUseful: str = None
    url: HttpUrl

class FeedbackWithHighlights(FeedbackBasePydantic):
    highlights: List[CompleteHighlight]

class FeedbackRating(BaseModel):
    performance: int
    clarity: int
    personalise: int
    evaluativeJudgement: int
    usability: int
    emotion: int
    furtherQuestions: str
    comment: str