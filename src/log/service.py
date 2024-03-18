from sqlalchemy.orm import Session
from src.log.schemas import Item
from uuid import uuid4

from .models import Log

localDatabase = []


def get_all_logs(db: Session):
    logs = db.query(Log).all()
   
    return logs


def create_log(db: Session, body:Item):

    new_log = Log(id=uuid4().hex, userEmail=body.userEmail, eventType=body.eventType, tagName=body.tagName, content=body.content,
                  baseUrl=body.baseUrl, ipAddress=body.ipAddress, rowStatus="ACTIVE" )

    db.add(new_log)

    db.commit()
    return new_log