from typing import List
from .schemas import ExplainFutherContentPydantic,ResponseExplain, CommonThemeResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.openai import service
from src.login.service import get_current_user
from src.feedback.models import Feedback
from src.highlight.models import Highlight
import json

router = APIRouter()

@router.post("/explain/{feedback_id}", response_model=ResponseExplain)
def explain_further(feedback_id: int,content:ExplainFutherContentPydantic, db: Session = Depends(get_db), user=Depends(get_current_user)):

    prompt_one = "Students receive feedback on their assessments and can manage this feedback using our tool that allows them to annotate, take notes, create action plans, and monitor their progress. However, some sentences in the feedback may be unclear or too complex, making it difficult for students to understand. "\
                "\nThe whole feedback that they receive is: feedback_text_prompt "\
                "\nYour task is to explain/clarify the feedback in a simpler way for the students to easily understand. When you explain the feedback make sure to use plain language and simple sentences, provide examples whenever possible and use bullet points to highlight key points."

    prompt_two = "The explanation received earlier not clear. Can you please go through the original feedback text again and provide an explanation / clarification in bullet points using plain language and simple sentences. This time, please make sure to include some actionable information, such as steps to take to improve learning."\
                "\n\nOriginal Feedback: feedback_text_prompt"


    query = prompt_one.replace("feedback_text_prompt", content.content)

    if content.attemptTime == 2:
        updated_feedback = db.query(Feedback.gptResponse, Feedback.gptQueryText).filter(
            Feedback.id == feedback_id,
            Feedback.studentEmail == user.email
        ).first()
        if updated_feedback:
            gpt_response,gptQueryText = updated_feedback
            query = prompt_two.replace("feedback_text_prompt", gpt_response)

    response = service.explain_further(query)
    if response:
        try:
            
            # Update the Feedback entry
            if content.attemptTime == 1:
                db.query(Feedback).filter(Feedback.id == feedback_id,Feedback.studentEmail == user.email).update(
                    {
                        Feedback.gptResponse: response.content,
                        Feedback.gptQueryText: content.content
                    }, synchronize_session='fetch')
            else:
                db.query(Feedback).filter(Feedback.id == feedback_id,Feedback.studentEmail == user.email).update(
                    {
                        Feedback.gptResponse_2: response.content,
                        Feedback.gptQueryText_2: content.content
                    }, synchronize_session='fetch')
            
            db.commit()
            

            return response
        except Exception as e:
            db.rollback()
    # Log the exception e
            raise HTTPException(status_code=500, detail="An error occurred while updating the database.")
        
@router.get("/common-theme", response_model=bool)
def explain_further(db: Session = Depends(get_db), user=Depends(get_current_user)):
    data_input = ""
    list_input = ""

    # Query to get only highlight ID and text where the feedback belongs to the logged-in user
    commonThemes = db.query(Highlight.commonTheme)\
                     .join(Feedback, Feedback.id == Highlight.feedbackId)\
                     .filter((Feedback.studentEmail != user.email) & (Highlight.commonTheme.isnot(None)))\
                     .all()

    # Query to get only highlight ID and text where the feedback belongs to the logged-in user
    highlights = db.query(Highlight.id, Highlight.text, Highlight.commonTheme)\
                   .join(Feedback, Feedback.id == Highlight.feedbackId)\
                   .filter((Feedback.studentEmail == user.email) & (Highlight.commonTheme == None))\
                   .all()
    
    if len(highlights) == 0:
        return True

    for commonTheme in commonThemes:
        if commonTheme[0]:  # Adjusted to handle tuple from query result
            list_input += f"{commonTheme[0]},"

    for highlight in highlights:
        print(f"Highlight id: {highlight.id} highlight: {highlight.text}\n")
        data_input += f"Highlight id: {highlight.id} highlight: {highlight.text}\n"

    prompt =    f"Data: {data_input} \nTask: Include the strengths into the matching categories of the following list of common themes. If there is no category to include, add a new one. Under each common theme specify the row number and the description."\
                "\nPlease provide the output in JSON array format: [{highlightId: {id}, commonTheme: {commonTheme}}]"
    try:
        # Simulate external service call
        response = service.explain_further(prompt)

        cleaned_content = response.content.replace('```json', '').replace('```', '').strip()

        results = json.loads(cleaned_content)

        for result in results:
            print(f"Highlight ID: {result['highlightId']}, Common Theme: {result['commonTheme']}")
            db.query(Highlight)\
              .filter(Highlight.id == result['highlightId'])\
              .update(
                  {Highlight.commonTheme: result['commonTheme']},
                  synchronize_session='fetch'
              )
        db.commit()
        return True
    except Exception as e:
        print(f"Error updating database: {e}")
        db.rollback()
        # raise HTTPException(status_code=500, detail="Internal Server Error") from e
        return False

