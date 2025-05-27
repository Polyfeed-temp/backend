#!/usr/bin/env python3
"""
Service Rollback Script

This script reverts the service.py file to its original non-encrypted version.
Run this AFTER rolling back the database encryption.

Usage:
    python service_rollback.py backup-service
    python service_rollback.py rollback-service
"""

import sys
import os
import shutil
from datetime import datetime

def backup_current_service():
    """Create a backup of the current encrypted service.py"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"service_encrypted_backup_{timestamp}.py"
    
    try:
        shutil.copy("service.py", backup_file)
        print(f"✅ Current service.py backed up to: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def rollback_service():
    """Rollback service.py to original non-encrypted version"""
    
    original_service_content = '''from enum import Enum

from sqlalchemy.orm import Session
from .models import User
from .schemas import UserPydantic
from src.dependencies import get_password_hash
from src.unit.models import Unit
from src.assessment.models import Assessment
from src.enrollment.models import Enrollment


def get_user_by_email(db: Session, email: str, no_password: bool = True):
    query = db.query(User)
    if no_password:
        query = query.filter(User.email == email).with_entities(
            User.email, User.role, User.faculty, User.monashId, 
            User.monashObjectId, User.authcate, User.lastName, User.firstName
        )
    else:
        query = query.filter(User.email == email)
    
    db_user = query.first()
    return db_user


def create_user(db: Session, userData: UserPydantic):
    # Convert Pydantic model to dict and handle enums
    user_dict = userData.model_dump()
    user_dict['role'] = userData.role.value
    user_dict['faculty'] = userData.faculty.value
    user_dict['monashObjectId'] = None
    
    db_user = User(**user_dict)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def signup_user(db: Session, userData: UserPydantic):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == userData.email).first()
    
    if db_user:
        return False
    else:
        # Hash the password and prepare user data
        user_dict = userData.model_dump()
        user_dict['password'] = get_password_hash(userData.password)
        user_dict['role'] = userData.role.value
        user_dict['faculty'] = userData.faculty.value
        user_dict['monashObjectId'] = None
        
        db_user = User(**user_dict)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user


def get_users(db: Session):
    users = db.query(User).all()
    return users


def update_user(db: Session, userData: UserPydantic, email: str):
    db_user = db.query(User).filter(User.email == email).first()
    
    if db_user:
        # Prepare update data
        update_data = userData.model_dump()
        
        for field, value in update_data.items():
            if hasattr(db_user, field):
                # Handle enum fields
                if isinstance(getattr(User, field).type, Enum):
                    value = getattr(User, field).type(value)
                setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        
        return db_user
    else:
        return None


def delete_user(db: Session, email: str):
    db_user = db.query(User).filter(User.email == email).first()
    
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    else:
        return False


def get_student_all_student_enrolled_units(db: Session, student_email: str):
    # Fetch the rows
    results = db.query(
        Unit.unitCode,
        Assessment.assessmentName,
        Assessment.id
    ).join(
        Enrollment, Enrollment.unitCode == Unit.unitCode
    ).join(
        Assessment, Unit.unitCode == Assessment.unitCode
    ).filter(
        Enrollment.userEmail == student_email
    ).all()

    # Process the results
    units = {}
    for unitCode, assessmentName, assessmentId in results:
        if unitCode not in units:
            units[unitCode] = {'unitCode': unitCode, 'assessments': []}
        units[unitCode]['assessments'].append({'assessmentName': assessmentName, 'id': assessmentId})

    return list(units.values())
'''
    
    try:
        with open("service.py", "w") as f:
            f.write(original_service_content)
        print("✅ service.py rolled back to original non-encrypted version")
        return True
    except Exception as e:
        print(f"❌ Service rollback failed: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python service_rollback.py backup-service")
        print("  python service_rollback.py rollback-service")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup-service":
        if backup_current_service():
            print("Service backup completed successfully!")
        else:
            print("Service backup failed!")
            sys.exit(1)
    elif command == "rollback-service":
        if rollback_service():
            print("Service rollback completed successfully!")
            print("\\n⚠️  Remember to restart your application!")
        else:
            print("Service rollback failed!")
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 