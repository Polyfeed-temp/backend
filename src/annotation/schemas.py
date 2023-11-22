from pydantic import BaseModel, HttpUrl, UUID4
from typing import Optional
from datetime import date
from .enums import AnnotationTag, ActionPointCategory
import json


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
    notes: Optional[str]

class FeedbackHighlightPydantic(BaseModel):
    unitCode: str
    assignment: str
    annotation: HighlightPydantic


class AnnotationActionPointPydantic(BaseModel):
    id: int
    action: str
    actionPoint: ActionPointCategory
    deadline: date
    annotationId: UUID4

# Example usage of parsing JSON to Pydantic model
# highlight_json = '{"id": "uuid", "start_meta": {...}, "end_meta": {...}, "text": "example", "url": "http://example.com", "annotation_tag": "Strength", "notes": "example notes"}'
# highlight = HighlightPydantic.parse_raw(highlight_json)
