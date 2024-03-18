from typing import List, Union
from pydantic import UUID4,BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.database import get_db
from src.login.service import get_current_user
from src.log.service import create_log, get_all_logs
from src.log.schemas import Item
router = APIRouter()



@router.post("/")
def create_logs(request: Request,item:Item, db: Session = Depends(get_db), user=Depends(get_current_user)): 
    client_host = request.client.host
    item.userEmail = user.email
    item.ipAddress = client_host
    return create_log(db, item)

@router.get("/")
# def create_logs(Item, db: Session = Depends(get_db), user=Depends(get_current_user)):
def get_logs( db: Session = Depends(get_db)):
    return get_all_logs(db)