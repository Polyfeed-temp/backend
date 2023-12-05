from datetime import date
from typing import Optional, List

from pydantic import BaseModel, HttpUrl, UUID4

from .enums import AnnotationTag

from src.action.schemas import ActionPydantic


class DomMeta(BaseModel):
    parentTagName: str
    parentIndex: int
    textOffset: int


class HighlightPydantic(BaseModel):
    id: UUID4
    startMeta: DomMeta
    endMeta: DomMeta
    text: str
    annotationTag: AnnotationTag
    notes: Optional[str] = None
    feedbackId: int
    gptResponse: Optional[str] = None

class CompleteHighlight(HighlightPydantic):
    annotation:HighlightPydantic
    actionItems: List[ActionPydantic]

