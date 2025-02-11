from sqlalchemy.orm import Session
from .models import FeedbackRequest
from .schemas import FeedbackRequestPydantic
from src.openai.service import explain_further
import json

def generate_ai_feedback(rubric_items, previous_feedback):
    # Convert RubricItems to dict for JSON serialization
    rubric_items_dict = [item.model_dump() for item in rubric_items]
    
    # Prompt for AI analysis
    rubric_prompt = f"""
    You are given a dataset with student feedback requests for <unit code> <unit name>, which specifies the rubric items and their specific feedback requests. In some cases, the rubric item is not mentioned, or the feedback request is very general. Your task is to generate two summaries: 
    Summary Table: 
    Create a table that shows the number of feedback requests per category. 
    For each category, include a brief description of the type of feedback requests typically found in that category. 
    List of Feedback Requests: 
    List the feedback requests under their corresponding rubric item or category. 
    If the rubric item is not mentioned or the request is very general, categorize it under a new category that reflects the request. 
    Organize the list so that each rubric item or category has a list of the feedback requests associated with it. 
    The feedback request categories should be based on common rubric items or, if unspecified, under new categories that capture the nature of the feedback request. 

    Return the two summaries as JSON files: 
    The first file should contain a summary table with the following structure: [ {{ "category": "Category Name", "feedback_count": Number of feedback requests in this category, "description": "Brief description of the types of feedback in this category" }} ] 
    The second file should contain a list of feedback requests, categorized under their rubric items or new categories: {{ "Category Name": [ "Feedback Request 1", "Feedback Request 2", ... ] }}

    Ensure the summaries are well-structured and easy to understand. 
    Data Set: {json.dumps(rubric_items_dict)}
    Previous feedback: {previous_feedback}
    """
    ai_response = explain_further(rubric_prompt)
    print("ai_response", ai_response)

    # Extract the two JSON objects from the response
    content = ai_response.content
    json_strings = content.split('```json\n')[1:]  # Split and remove the first empty part
    json_strings = [s.split('```')[0].strip() for s in json_strings]  # Remove the closing ```

    # Parse both JSON objects
    summary_table = json_strings[0]  # First JSON object (summary table)
    feedback_requests = json_strings[1]  # Second JSON object (feedback requests)

    return summary_table, feedback_requests

def create_feedback_request(db: Session, request: FeedbackRequestPydantic, student_id: str):
    # Generate AI feedback
    summary_response, categorized_response = generate_ai_feedback(
        request.rubricItems,
        request.previousFeedbackUsage
    )

    # Convert RubricItems to dict for JSON serialization
    rubric_items_dict = [item.model_dump() for item in request.rubricItems]

    new_request = FeedbackRequest(
        assignmentId=request.assignmentId,
        rubricItems=json.dumps(rubric_items_dict),  # Store as JSON string
        previousFeedbackUsage=request.previousFeedbackUsage,
        AI_RubricItem=summary_response,      # Store summary table JSON
        AI_FBRequest=categorized_response,   # Store feedback requests JSON
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