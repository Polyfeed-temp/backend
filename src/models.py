from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects import postgresql as types

Base  = declarative_base()

"""
highlightsource {
endMeta: {parentTagName: 'P', parentIndex: 0, textOffset: 93},
id: "f48d3a64-8383-4209-b6a0-543689915ef5"
startMeta:{parentTagName: 'P', parentIndex: 0, textOffset: 22}
text: "test" }
"""
class HighlightSource(Base):
    __tablename__ = 'highlight_source'

    id = Column(types.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Storing startMeta and endMeta as JSON columns
    startMeta = Column(JSON)
    endMeta = Column(JSON)
    text = Column(String)

