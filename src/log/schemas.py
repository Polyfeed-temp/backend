from typing import Union
from pydantic import UUID4, BaseModel, Field

class Item(BaseModel):
    eventType: str = Field(gt="", description="The price must be greater than zero")
    tagName: str = None
    content: Union[str, None] = None
    baseUrl: str = None
    userEmail :str = None
    ipAddress:str= None