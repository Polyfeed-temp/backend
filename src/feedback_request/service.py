from sqlalchemy.orm import Session
from .models import FeedbackRequest
from .schemas import FeedbackRequestPydantic
from src.openai.service import explain_further
import json

def generate_ai_feedback(rubric_items, previous_feedback):
    # Convert RubricItems to dict for JSON serialization
    rubric_items_dict = [item.model_dump() for item in rubric_items]
    
    # Prompt for AI_RubricItem
    rubric_prompt = f"""
    Based on these rubric items: {json.dumps(rubric_items_dict)}
    And previous feedback usage: {previous_feedback}
    Please analyze the rubric items and provide detailed feedback suggestions.
    """
    ai_rubric_response = explain_further(rubric_prompt)

    # Prompt for AI_FBRequest
    feedback_prompt = f"""
    Given the rubric items: {json.dumps(rubric_items_dict)}
    And previous feedback: {previous_feedback}
    Please generate a comprehensive feedback request that addresses all rubric items.
    Focus on areas that need improvement and specific suggestions.
    """
    ai_feedback_response = explain_further(feedback_prompt)

    return ai_rubric_response.content, ai_feedback_response.content

def create_feedback_request(db: Session, request: FeedbackRequestPydantic, student_id: str):
    # Generate AI feedback
    ai_rubric, ai_feedback = generate_ai_feedback(
        request.rubricItems,
        request.previousFeedbackUsage
    )

    # Convert RubricItems to dict for JSON serialization
    rubric_items_dict = [item.model_dump() for item in request.rubricItems]

    new_request = FeedbackRequest(
        assignmentId=request.assignmentId,
        rubricItems=json.dumps(rubric_items_dict),  # Store as JSON string
        previousFeedbackUsage=request.previousFeedbackUsage,
        AI_RubricItem=ai_rubric,
        AI_FBRequest=ai_feedback,
        student_id=student_id
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    # Convert the response
    response = FeedbackRequestPydantic(
        id=new_request.id,
        assignmentId=new_request.assignmentId,
        rubricItems=new_request.get_rubric_items(),
        previousFeedbackUsage=new_request.previousFeedbackUsage,
        AI_RubricItem=new_request.AI_RubricItem,
        AI_FBRequest=new_request.AI_FBRequest,
        student_id=new_request.student_id
    )
    return response

def get_feedback_requests(db: Session, student_id: str, skip: int = 0, limit: int = 100):
    requests = db.query(FeedbackRequest)\
        .filter(FeedbackRequest.student_id == student_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Convert each request to the Pydantic model
    return [FeedbackRequestPydantic(
        id=req.id,
        assignmentId=req.assignmentId,
        rubricItems=req.get_rubric_items(),
        previousFeedbackUsage=req.previousFeedbackUsage,
        AI_RubricItem=req.AI_RubricItem,
        AI_FBRequest=req.AI_FBRequest,
        student_id=req.student_id
    ) for req in requests] 