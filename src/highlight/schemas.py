from datetime import date
from typing import Optional, List, Union

from pydantic import BaseModel, HttpUrl, UUID4

from .enums import AnnotationTag

from src.action.schemas import ActionPydantic


class DomMeta(BaseModel):
    parentTagName: str
    parentIndex: int
    textOffset: int


class HighlightPydantic(BaseModel):
    id: Union[UUID4, str]
    startMeta: DomMeta
    endMeta: DomMeta
    text: str
    annotationTag: AnnotationTag
    notes: Optional[str] = None
    feedbackId: int
    gptResponse: Optional[str] = None
    commonTheme: Optional[str] = None

class CompleteHighlight(BaseModel):
    annotation:HighlightPydantic
    actionItems: Optional[List[ActionPydantic]] = None

