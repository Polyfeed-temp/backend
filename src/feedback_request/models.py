from sqlalchemy import Table, Column, Integer, String, JSON, ForeignKey
from src.base import get_base
from src.database import engine

Base = get_base()

class FeedbackRequest(Base):
    __tablename__ = "FEEDBACK_REQUESTS"
    
    id = Column(Integer, primary_key=True, index=True)
    assignmentId = Column(Integer)
    rubricItems = Column(JSON)
    previousFeedbackUsage = Column(String)
    aiRubricItems = Column(JSON, nullable=True)
    AI_RubricItem  = Column(String, nullable=True) 
    AI_FBRequest = Column(String, nullable=True)