from pydantic import BaseModel
from typing import Optional, List
from pydantic import HttpUrl
from src.highlight.schemas import HighlightWithActions


class FeedbackBasePydantic(BaseModel):
    id: Optional[int] = None
    mark: int
    clarity: Optional[int] = None
    personalise: Optional[int] = None
    usability: Optional[int] = None
    emotion: Optional[int] = None
    markerEmail: Optional[str] = None
    studentEmail: str
    assessmentId: int
    url: HttpUrl

class FeedbackWithHighlights(FeedbackBasePydantic):
    highlights: List[HighlightWithActions]


