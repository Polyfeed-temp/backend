from pydantic import BaseModel


class UnitPydantic(BaseModel):
    unitCode: str
    unitName: str
