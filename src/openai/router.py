from typing import List
from .schemas import ExplainFutherContentPydantic
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.openai import service


router = APIRouter()

router.post("/explain_further", response_model=ExplainFutherContentPydantic)
def explain_further(content:ExplainFutherContentPydantic):
    return service.explain_further(content)
