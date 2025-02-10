from sqlalchemy.orm import Session
from .models import FeedbackRequest
from .schemas import FeedbackRequestCreate, FeedbackRequestResponse
from src.openai.service import explain_further
import json

def generate_ai_feedback(rubric_items, previous_feedback):
    # Prompt for AI_RubricItem
    rubric_prompt = f"""
    Based on these rubric items: {json.dumps(rubric_items)}
    And previous feedback usage: {previous_feedback}
    Please analyze the rubric items and provide detailed feedback suggestions.
    """
    ai_rubric_response = explain_further(rubric_prompt)

    # Prompt for AI_FBRequest
    feedback_prompt = f"""
    Given the rubric items: {json.dumps(rubric_items)}
    And previous feedback: {previous_feedback}
    Please generate a comprehensive feedback request that addresses all rubric items.
    Focus on areas that need improvement and specific suggestions.
    """
    ai_feedback_response = explain_further(feedback_prompt)

    return ai_rubric_response.content, ai_feedback_response.content

def create_feedback_request(db: Session, request: FeedbackRequestCreate):
    # Generate AI feedback
    ai_rubric, ai_feedback = generate_ai_feedback(
        request.model_dump()["rubricItems"],
        request.previousFeedbackUsage
    )

    db_request = FeedbackRequest(
        assignmentId=request.assignmentId,
        rubricItems=request.model_dump()["rubricItems"],
        previousFeedbackUsage=request.previousFeedbackUsage,
        AI_RubricItem=ai_rubric,
        AI_FBRequest=ai_feedback
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def get_feedback_requests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(FeedbackRequest).offset(skip).limit(limit).all() 