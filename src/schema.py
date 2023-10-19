from pydantic import BaseModel, UUID4



class DomMeta(BaseModel):
    parentTagName: str
    parentIndex: int
    textOffset: int

"""
highlightsource {
endMeta: {parentTagName: 'P', parentIndex: 0, textOffset: 93},
id: "f48d3a64-8383-4209-b6a0-543689915ef5"
startMeta:{parentTagName: 'P', parentIndex: 0, textOffset: 22}
text: "test" }
"""
class HighlighSource(BaseModel):
    id: UUID4
    startMeta: DomMeta
    endMeta: DomMeta
    text: str

    class Config:
        orm_mode =True
