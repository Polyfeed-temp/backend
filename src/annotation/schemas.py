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
    start_meta: DomMeta
    end_meta: DomMeta
    text: str
    url: HttpUrl
    annotation_tag: AnnotationTag
    notes: Optional[str]

class AnnotationActionPointPydantic(BaseModel):
    id: int
    action: str
    actionpoint: ActionPointCategory
    deadline: date
    annotation_id: UUID4

# Example usage of parsing JSON to Pydantic model
# highlight_json = '{"id": "uuid", "start_meta": {...}, "end_meta": {...}, "text": "example", "url": "http://example.com", "annotation_tag": "Strength", "notes": "example notes"}'
# highlight = HighlightPydantic.parse_raw(highlight_json)
