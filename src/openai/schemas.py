from pydantic import BaseModel

class ExplainFutherContentPydantic(BaseModel):
    content: str
    attemptTime:int


class ResponseExplain(BaseModel):
    content: str
