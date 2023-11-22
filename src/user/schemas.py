from pydantic import BaseModel
from typing import ClassVar


class UserPydantic(BaseModel):
    id: int
    monashId: str
    monashObjectId: str
    authcate: str
    email: str
    lastName: str
    firstName: str

# Example usage of parsing JSON to Pydantic model
# highlight_json = '{"id": "uuid", "start_meta": {...}, "end_meta": {...}, "text": "example", "url": "http://example.com", "annotation_tag": "Strength", "notes": "example notes"}'
# highlight = HighlightPydantic.parse_raw(highlight_json)
