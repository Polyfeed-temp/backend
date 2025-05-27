from sqlalchemy.orm import Session
from .models import FeedbackRequest
from .schemas import FeedbackRequestPydantic
from src.openai.service import explain_further
from src.assessment.models import Assessment
from src.user.encryption import encrypt_field, decrypt_field
import json

def get_existing_feedback_requests(db: Session, assignment_id: int):
    """Get existing feedback requests for an assignment"""
    return db.query(FeedbackRequest)\
        .filter(FeedbackRequest.assignmentId == assignment_id)\
        .all()

def generate_ai_feedback(db: Session, rubric_items, assignment_id: int):
    # Convert RubricItems to dict for JSON serialization and limit to 10 items
    rubric_items_dict = [item.model_dump() for item in rubric_items][-10:]
    
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
        # Create Dataset B from existing requests (limited to 10 items)
        existing_data = []
        for req in existing_requests[-10:]:
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

def _encrypt_feedback_request_emails(data: dict) -> dict:
    """Encrypt email fields in feedback request data before storage."""
    encrypted_data = data.copy()
    
    # Encrypt student_id field (which contains email)
    if 'student_id' in encrypted_data and encrypted_data['student_id']:
        encrypted_data['student_id'] = encrypt_field(encrypted_data['student_id'])
    
    return encrypted_data

def _decrypt_feedback_request_emails(feedback_request_obj) -> dict:
    """Decrypt email fields when retrieving feedback request from database."""
    if hasattr(feedback_request_obj, '__dict__'):
        # Convert SQLAlchemy object to dict
        data_dict = {column.name: getattr(feedback_request_obj, column.name) for column in feedback_request_obj.__table__.columns}
    elif hasattr(feedback_request_obj, '_asdict'):
        # SQLAlchemy Row object
        data_dict = feedback_request_obj._asdict()
    elif hasattr(feedback_request_obj, 'keys'):
        # Dict-like object
        data_dict = dict(feedback_request_obj)
    else:
        # Convert to dict manually
        data_dict = {}
        for key in dir(feedback_request_obj):
            if not key.startswith('_'):
                try:
                    data_dict[key] = getattr(feedback_request_obj, key)
                except:
                    pass
    
    # Decrypt student_id field
    if 'student_id' in data_dict and data_dict['student_id']:
        try:
            data_dict['student_id'] = decrypt_field(data_dict['student_id'])
        except:
            pass  # If decryption fails, keep original value
    
    return data_dict

def _find_feedback_request_by_encrypted_email(db: Session, email: str, assignment_id: int = None) -> FeedbackRequest:
    """Find feedback request by searching through encrypted emails."""
    query = db.query(FeedbackRequest)
    if assignment_id:
        query = query.filter(FeedbackRequest.assignmentId == assignment_id)
    
    requests = query.all()
    
    for request in requests:
        try:
            decrypted_email = decrypt_field(request.student_id)
            if decrypted_email == email:
                return request
        except:
            # If decryption fails, check if it's already unencrypted
            if request.student_id == email:
                return request
    
    return None

def create_feedback_request(db: Session, request: FeedbackRequestPydantic, student_id: str):
    # Check if request already exists for this assignment and student using encrypted search
    existing_request = _find_feedback_request_by_encrypted_email(db, student_id, request.assignmentId)

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
        
        # Decrypt data for response
        decrypted_request = _decrypt_feedback_request_emails(existing_request)
        
        response = FeedbackRequestPydantic(
            id=decrypted_request["id"],
            assignmentId=decrypted_request["assignmentId"],
            rubricItems=existing_request.get_rubric_items(),
            AI_RubricItem=decrypted_request["AI_RubricItem"],
            student_id=decrypted_request["student_id"]
        )
        return response
    else:
        # Create new request with encrypted data
        encrypted_data = _encrypt_feedback_request_emails({'student_id': student_id})
        
        new_request = FeedbackRequest(
            assignmentId=request.assignmentId,
            rubricItems=json.dumps(rubric_items_dict),
            AI_RubricItem=ai_rubric_response,
            student_id=encrypted_data['student_id']
        )
        
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        
        # Decrypt data for response
        decrypted_request = _decrypt_feedback_request_emails(new_request)
        
        response = FeedbackRequestPydantic(
            id=decrypted_request["id"],
            assignmentId=decrypted_request["assignmentId"],
            rubricItems=new_request.get_rubric_items(),
            AI_RubricItem=decrypted_request["AI_RubricItem"],
            student_id=decrypted_request["student_id"]
        )
        return response

def get_feedback_requests(db: Session, student_id: str, skip: int = 0, limit: int = 100):
    # Get all requests and filter by decrypted email
    all_requests = db.query(FeedbackRequest, Assessment)\
        .join(Assessment, FeedbackRequest.assignmentId == Assessment.id)\
        .offset(skip)\
        .limit(limit * 10)\
        .all()
    
    result = []
    count = 0
    
    for req, assessment in all_requests:
        if count >= limit:
            break
            
        try:
            decrypted_email = decrypt_field(req.student_id)
            email_matches = (decrypted_email == student_id)
        except:
            # If decryption fails, check if it's already unencrypted
            email_matches = (req.student_id == student_id)
        
        if email_matches:
            decrypted_request = _decrypt_feedback_request_emails(req)
            
        feedback_request = FeedbackRequestPydantic(
                id=decrypted_request["id"],
                assignmentId=decrypted_request["assignmentId"],
            rubricItems=req.get_rubric_items(),
                AI_RubricItem=decrypted_request["AI_RubricItem"],
                student_id=decrypted_request["student_id"],
            assessment={
                "id": assessment.id,
                "name": assessment.assessmentName,
                "unitId": assessment.unitId,
            }
        )
        result.append(feedback_request)
            count += 1
    
    return result

def get_feedback_request_by_assignment(db: Session, assignment_id: int, student_id: str):
    """Get a single feedback request for a specific assignment and student"""
    # Find request using encrypted email search
    request = _find_feedback_request_by_encrypted_email(db, student_id, assignment_id)
    
    if not request:
        return None
    
    # Get assessment info
    assessment = db.query(Assessment).filter(Assessment.id == assignment_id).first()
    if not assessment:
        return None
    
    # Decrypt request data
    decrypted_request = _decrypt_feedback_request_emails(request)
        
    return FeedbackRequestPydantic(
        id=decrypted_request["id"],
        assignmentId=decrypted_request["assignmentId"],
        rubricItems=request.get_rubric_items(),
        AI_RubricItem=decrypted_request["AI_RubricItem"],
        student_id=decrypted_request["student_id"],
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
        # Decrypt request data
        decrypted_request = _decrypt_feedback_request_emails(request)
        
        feedback_requests.append(FeedbackRequestPydantic(
            id=decrypted_request["id"],
            assignmentId=decrypted_request["assignmentId"],
            rubricItems=request.get_rubric_items(),
            AI_RubricItem=decrypted_request["AI_RubricItem"],
            student_id=decrypted_request["student_id"],
            assessment={
                "id": assessment.id,
                "name": assessment.assessmentName,
                "unitId": assessment.unitId,
            }
        ))
    
    return feedback_requests
    