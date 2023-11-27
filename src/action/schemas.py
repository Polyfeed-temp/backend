from datetime import date

from pydantic import BaseModel, UUID4

from .enums import ActionPointCategory


class ActionPydantic(BaseModel):
    id: int
    action: str
    category: ActionPointCategory
    deadline: date
    highlightId: UUID4
