from datetime import date
from typing import Optional

from pydantic import BaseModel, HttpUrl, UUID4

from .enums import AnnotationTag


class DomMeta(BaseModel):
    parentTagName: str
    parentIndex: int
    textOffset: int


class HighlightPydantic(BaseModel):
    id: UUID4
    startMeta: DomMeta
    endMeta: DomMeta
    text: str
    url: HttpUrl
    annotationTag: AnnotationTag
    notes: Optional[str] = None
    feedbackId: int
