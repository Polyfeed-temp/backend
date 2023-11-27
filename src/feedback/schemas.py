from pydantic import BaseModel


class FeedbackPydantic(BaseModel):
    id: int
    mark: int
    clarity: int
    personlise: int
    usability: int
    emotion: int
    markerEmail: str
    studentEmail: str
    assessmentId: int