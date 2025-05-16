from sqlalchemy.orm import Session
from .models import FeedbackRequest
from .schemas import FeedbackRequestPydantic
from src.openai.service import explain_further
from src.assessment.models import Assessment
import json

def get_existing_feedback_requests(db: Session, assignment_id: int):
    """Get existing feedback requests for an assignment"""
    return db.query(FeedbackRequest)\
        .filter(FeedbackRequest.assignmentId == assignment_id)\
        .all()

def generate_ai_feedback(db: Session, rubric_items, assignment_id: int):
    # Convert RubricItems to dict for JSON serialization and limit to 100 items
    rubric_items_dict = [item.model_dump() for item in rubric_items][:100]
    
    # Check if this is the first time for this assignment
    existing_requests = get_existing_feedback_requests(db, assignment_id)
    
    if not existing_requests:
        # First time prompt
        first_time_prompt = {
          "task": "Generate AI_Rubric Items for student feedback requests",
          "context": {
            "unit": "<unit code> <unit name>",
            "description": "This is the first time the student is requesting feedback for this assignment.",
            "assignment_id": assignment_id,
            "dataset_format": ["Rubric Item", "Feedback Request"]
          },
          "instructions": [
            "For each entry in the dataset, generate a concise and meaningful AI_RubricItem based on the 'Rubric Item' and 'Feedback Request'.",
            "Add a new column named 'AI_RubricItem' to the dataset.",
            "Each AI_RubricItem must not exceed 8 words in the 'item' field.",
            "If the input is vague, general, or partially missing, still try to infer a useful AI_RubricItem if possible.",
            "If the input is nonsensical or meaningless (e.g., random characters or numbers like 'asdf', '1234', 'kkkk'), set item to 'Unmappable' and leave comments field empty."
          ],
          "examples_of_nonsensical_input": [
            "Random strings (e.g., 'asdf', 'kkkk')",
            "Isolated numbers (e.g., '1234', '2323')",
            "Keyboard mashing (e.g., 'qwertyui')",
            "Empty or whitespace-only fields",
            "Words or phrases with no educational context (e.g., 'banana', 'lol')"
          ],
          "exact_output_format": [
            {
              "item": "Original Rubric Item",
              "comments": "Original Feedback Request",
              "AI_RubricItem": {
                "item": "Short concise rubric title (max 8 words)",
                "comments": "Clarified version of the request or empty string if Unmappable"
              }
            }
          ],
          "dataset": rubric_items_dict
        }
        
        prompt = f"""
        {json.dumps(first_time_prompt, indent=2)}
        
        IMPORTANT: Your response MUST be in the following JSON format enclosed in ```json blocks:
        
        ```json
        [
            {{
                "item": "Original item from input",
                "comments": "Original comments from input",
                "AI_RubricItem": {{
                    "item": "Concise rubric title (max 8 words)",
                    "comments": "Clarified version of the request"
                }}
            }},
            ...more items...
        ]
        ```
        
        When item is "Unmappable", the comments field MUST be an empty string ("").
        """
    else:
        # Create Dataset B from existing requests (limited to 100 items)
        existing_data = []
        for req in existing_requests[:100]:
            existing_data.append({
                "AI_RubricItem": req.AI_RubricItem
            })

        # Subsequent times prompt
        subsequent_prompt = {
          "task": "Generate AI_Rubric Items for student feedback requests",
          "context": {
            "unit": "<unit code> <unit name>",
            "description": "The student is requesting feedback for an assignment with existing feedback requests.",
            "assignment_id": assignment_id,
            "dataset_format": ["Rubric Item", "Feedback Request"]
          },
          "instructions": [
            "For each entry in Dataset A, generate a concise and meaningful AI_RubricItem based on the 'Rubric Item' and 'Feedback Request'.",
            "When possible, map new entries to existing AI_RubricItems from Dataset B for consistency.",
            "If a suitable match cannot be found in Dataset B, create a new AI_RubricItem.",
            "Each AI_RubricItem must not exceed 8 words in the 'item' field.",
            "If the input is vague, general, or partially missing, still try to infer a useful AI_RubricItem if possible.",
            "If the input is nonsensical or meaningless (e.g., random characters or numbers like 'asdf', '1234', 'kkkk'), set item to 'Unmappable' and leave comments field empty."
          ],
          "examples_of_nonsensical_input": [
            "Random strings (e.g., 'asdf', 'kkkk')",
            "Isolated numbers (e.g., '1234', '2323')",
            "Keyboard mashing (e.g., 'qwertyui')",
            "Empty or whitespace-only fields",
            "Words or phrases with no educational context (e.g., 'banana', 'lol')"
          ],
          "exact_output_format": [
            {
              "item": "Original Rubric Item",
              "comments": "Original Feedback Request",
              "AI_RubricItem": {
                "item": "Short concise rubric title (max 8 words)",
                "comments": "Clarified version of the request or empty string if Unmappable"
              }
            }
          ],
          "dataset_a": rubric_items_dict,
          "dataset_b": existing_data
        }
        
        prompt = f"""
        {json.dumps(subsequent_prompt, indent=2)}
        
        IMPORTANT: Your response MUST be in the following JSON format enclosed in ```json blocks:
        
        ```json
        [
            {{
                "item": "Original item from input",
                "comments": "Original comments from input",
                "AI_RubricItem": {{
                    "item": "Concise rubric title (max 8 words)",
                    "comments": "Clarified version of the request"
                }}
            }},
            ...more items...
        ]
        ```
        
        When item is "Unmappable", the comments field MUST be an empty string ("").
        """

    ai_response = explain_further(prompt)
    print("ai_response", ai_response)

    # Extract the JSON from the response
    content = ai_response.content
    try:
        # Try to find JSON block
        if '```json' in content:
            json_part = content.split('```json\n')[1].split('```')[0].strip()
        else:
            # If no JSON blocks, try to extract JSON directly
            json_part = content.strip()
        
        print("Extracted JSON:", json_part)
        
        # Validate it's proper JSON
        json.loads(json_part)  # This will raise an error if invalid JSON
        return json_part
        
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        # Return a simple JSON array as fallback
        return json.dumps([{"error": "Failed to parse AI response"}])

def create_feedback_request(db: Session, request: FeedbackRequestPydantic, student_id: str):
    # Check if request already exists for this assignment and student
    existing_request = db.query(FeedbackRequest)\
        .filter(
            FeedbackRequest.assignmentId == request.assignmentId,
            FeedbackRequest.student_id == student_id
        )\
        .first()

    # Generate AI feedback
    print("request.rubricItems", request.rubricItems)
    print("request.assignmentId", request.assignmentId)
    print("student_id", student_id)
    ai_rubric_response = generate_ai_feedback(
        db,
        request.rubricItems,
        request.assignmentId
    )

    # Convert RubricItems to dict for JSON serialization
    rubric_items_dict = [item.model_dump() for item in request.rubricItems]

    if existing_request:
        # Update existing request
        existing_request.rubricItems = json.dumps(rubric_items_dict)
        existing_request.AI_RubricItem = ai_rubric_response
        db.commit()
        db.refresh(existing_request)
        
        response = FeedbackRequestPydantic(
            id=existing_request.id,
            assignmentId=existing_request.assignmentId,
            rubricItems=existing_request.get_rubric_items(),
            AI_RubricItem=existing_request.AI_RubricItem,
            student_id=existing_request.student_id
        )
        return response
    else:
        # Create new request
        new_request = FeedbackRequest(
            assignmentId=request.assignmentId,
            rubricItems=json.dumps(rubric_items_dict),
            AI_RubricItem=ai_rubric_response,
            student_id=student_id
        )
        
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        
        response = FeedbackRequestPydantic(
            id=new_request.id,
            assignmentId=new_request.assignmentId,
            rubricItems=new_request.get_rubric_items(),
            AI_RubricItem=new_request.AI_RubricItem,
            student_id=new_request.student_id
        )
        return response

def get_feedback_requests(db: Session, student_id: str, skip: int = 0, limit: int = 100):
    requests = db.query(FeedbackRequest, Assessment)\
        .join(Assessment, FeedbackRequest.assignmentId == Assessment.id)\
        .filter(FeedbackRequest.student_id == student_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    result = []
    for req, assessment in requests:
        feedback_request = FeedbackRequestPydantic(
            id=req.id,
            assignmentId=req.assignmentId,
            rubricItems=req.get_rubric_items(),
            AI_RubricItem=req.AI_RubricItem,
            student_id=req.student_id,
            assessment={
                "id": assessment.id,
                "name": assessment.assessmentName,
                "unitId": assessment.unitId,
            }
        )
        result.append(feedback_request)
    
    return result

def get_feedback_request_by_assignment(db: Session, assignment_id: int, student_id: str):
    """Get a single feedback request for a specific assignment and student"""
    result = db.query(FeedbackRequest, Assessment)\
        .join(Assessment, FeedbackRequest.assignmentId == Assessment.id)\
        .filter(
            FeedbackRequest.assignmentId == assignment_id,
            FeedbackRequest.student_id == student_id
        )\
        .first()
    
    if not result:
        return None
    
    request, assessment = result
        
    return FeedbackRequestPydantic(
        id=request.id,
        assignmentId=request.assignmentId,
        rubricItems=request.get_rubric_items(),
        AI_RubricItem=request.AI_RubricItem,
        student_id=request.student_id,
        assessment={
            "id": assessment.id,
            "name": assessment.assessmentName,
            "description": assessment.description if hasattr(assessment, 'description') else None,
            "unit_id": assessment.unit_id if hasattr(assessment, 'unit_id') else None,
            # Add other assessment fields you want to include
        }
    ) 

def get_feedback_request_by_unitcode_assessment(db: Session, unit_code: str, assessment_name: str):
    """Get all feedback requests for a specific unit code and assessment name"""

    print("unit_code", unit_code)
    print("assessment_name", assessment_name)
    results = db.query(FeedbackRequest, Assessment)\
        .join(Assessment, FeedbackRequest.assignmentId == Assessment.id)\
        .filter(
            Assessment.unitId == unit_code,
            Assessment.assessmentName == assessment_name,
        )\
        .all()
    
    if not results:
        return []
    
    feedback_requests = []
    for request, assessment in results:
        feedback_requests.append(FeedbackRequestPydantic(
            id=request.id,
            assignmentId=request.assignmentId,
            rubricItems=request.get_rubric_items(),
            AI_RubricItem=request.AI_RubricItem,
            student_id=request.student_id,
            assessment={
                "id": assessment.id,
                "name": assessment.assessmentName,
                "unitId": assessment.unitId,
            }
        ))
    
    return feedback_requests
    