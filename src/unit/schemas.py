from pydantic import BaseModel


class UnitPydantic(BaseModel):
    unitCode: str
    unitName: str
    offering: str

# Example usage of parsing JSON to Pydantic model
# highlight_json = '{"id": "uuid", "start_meta": {...}, "end_meta": {...}, "text": "example", "url": "http://example.com", "annotation_tag": "Strength", "notes": "example notes"}'
# highlight = HighlightPydantic.parse_raw(highlight_json)
