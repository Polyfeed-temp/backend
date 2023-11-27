from pydantic import BaseModel
from typing_extensions import Annotated
from .enums import Role
from typing import  Optional


class UserPydantic(BaseModel):
    monashId: str
    monashObjectId: Optional[str] = None
    authcate: str
    email: str
    lastName: str
    firstName: str
    role: Role
    password: str
    faculty: str

# Example usage of parsing JSON to Pydantic model
# highlight_json = '{"id": "uuid", "start_meta": {...}, "end_meta": {...}, "text": "example", "url": "http://example.com", "annotation_tag": "Strength", "notes": "example notes"}'
# highlight = HighlightPydantic.parse_raw(highlight_json)
