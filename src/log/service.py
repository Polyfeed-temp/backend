from sqlalchemy.orm import Session
from src.log.schemas import Item
from uuid import uuid4
from src.user.encryption import encrypt_field, decrypt_field

from .models import Log

localDatabase = []


def get_all_logs(db: Session):
    logs = db.query(Log).all()
   
    # Decrypt userEmail fields for response
    decrypted_logs = []
    for log in logs:
        log_dict = {
            'id': log.id,
            'eventType': log.eventType,
            'content': log.content,
            'baseUrl': log.baseUrl,
            'eventSource': log.eventSource,
            'createdAt': log.createdAt,
            'updatedAt': log.updatedAt
        }
        
        # Decrypt userEmail
        if log.userEmail:
            try:
                log_dict['userEmail'] = decrypt_field(log.userEmail)
            except:
                log_dict['userEmail'] = log.userEmail  # If decryption fails, keep original
        else:
            log_dict['userEmail'] = log.userEmail
            
        decrypted_logs.append(log_dict)
   
    return decrypted_logs


def create_log(db: Session, body:Item):
    # Encrypt userEmail before storage
    encrypted_user_email = encrypt_field(body.userEmail) if body.userEmail else None

    new_log = Log(id=uuid4().hex, userEmail=encrypted_user_email, eventType=body.eventType, content=body.content,
                  baseUrl=body.baseUrl, eventSource=body.eventSource )

    db.add(new_log)
    db.commit()
    
    # Return decrypted data for response
    log_dict = {
        'id': new_log.id,
        'userEmail': body.userEmail,  # Return original unencrypted email
        'eventType': new_log.eventType,
        'content': new_log.content,
        'baseUrl': new_log.baseUrl,
        'eventSource': new_log.eventSource,
        'createdAt': new_log.createdAt,
        'updatedAt': new_log.updatedAt
    }
    
    return log_dict


def get_logs_by_user_email(db: Session, user_email: str):
    """Get logs for a specific user by searching through encrypted emails."""
    all_logs = db.query(Log).all()
    user_logs = []
    
    for log in all_logs:
        if log.userEmail:
            try:
                decrypted_email = decrypt_field(log.userEmail)
                if decrypted_email == user_email:
                    log_dict = {
                        'id': log.id,
                        'userEmail': decrypted_email,
                        'eventType': log.eventType,
                        'content': log.content,
                        'baseUrl': log.baseUrl,
                        'eventSource': log.eventSource,
                        'createdAt': log.createdAt,
                        'updatedAt': log.updatedAt
                    }
                    user_logs.append(log_dict)
            except:
                # If decryption fails, check if it's already unencrypted
                if log.userEmail == user_email:
                    log_dict = {
                        'id': log.id,
                        'userEmail': log.userEmail,
                        'eventType': log.eventType,
                        'content': log.content,
                        'baseUrl': log.baseUrl,
                        'eventSource': log.eventSource,
                        'createdAt': log.createdAt,
                        'updatedAt': log.updatedAt
                    }
                    user_logs.append(log_dict)
    
    return user_logs