from typing import Union
from pydantic import UUID4, BaseModel, Field

class Item(BaseModel):
    eventType: str = None
    content: Union[str, None] = None
    baseUrl: str = Field(None, max_length=4294967295)  # LONGTEXT max length
    userEmail :str = None
    ipAddress:str= None
    eventSource:str=None