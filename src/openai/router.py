from typing import List
from .schemas import ExplainFutherContentPydantic
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.openai import service
from src.login.service import get_current_user
from src.feedback.models import Feedback

router = APIRouter()

@router.post("/explain/{feedback_id}", response_model=ExplainFutherContentPydantic)
def explain_further(feedback_id: int,content:ExplainFutherContentPydantic, db: Session = Depends(get_db), user=Depends(get_current_user)):
    response = service.explain_further(content.content)
    if response:
        try:
        # Update the Feedback entry
            db.query(Feedback).filter(Feedback.id == feedback_id,
            Feedback.studentEmail == user.email).update(
        {
            Feedback.gptResponse: response.content,
            Feedback.gptQueryText: content.content
        },
            synchronize_session='fetch')
            db.commit()
            return response
        except Exception as e:
            db.rollback()
    # Log the exception e
            raise HTTPException(status_code=500, detail="An error occurred while updating the database.")


