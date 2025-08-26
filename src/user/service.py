from enum import Enum

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
        query = query.filter(User.email == email).with_entities(User.email, User.role, User.faculty, User.monashId, User.monashObjectId, User.authcate, User.lastName, User.firstName)
    else:
        query = query.filter(User.email == email)
    db_user = query.all()

    if len(db_user) == 1:
        return db_user[0]
    else:
        return None


def create_user(db: Session, userData: UserPydantic):
    userData.role = userData.role.value
    userData.faculty = userData.faculty.value
    userData.monashObjectId = None
    db_user = User(**userData.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def signup_user(db: Session, signupData):
    from .enums import Role, Faculty
    from .schemas import UserPydantic
    
    # Check if email and password are provided and not empty FIRST
    if not signupData.email or signupData.email.strip() == "":
        return None
    if not signupData.password or signupData.password.strip() == "":
        return None
    
    # Check if user exists with password
    db_user_with_password = db.query(User).filter(User.email == signupData.email, User.password != None, User.password != "").all()
    if len(db_user_with_password) == 1:
        return False  # User already exists with password
    
    # Check if user exists without password
    db_user_no_password = db.query(User).filter(User.email == signupData.email, (User.password == None) | (User.password == "")).first()
    if db_user_no_password:
        # Update existing user's password
        db_user_no_password.password = get_password_hash(signupData.password)
        db_user_no_password.firstName = signupData.firstName
        db_user_no_password.lastName = signupData.lastName
        if signupData.monashId:
            db_user_no_password.monashId = signupData.monashId
        db.commit()
        db.refresh(db_user_no_password)
        return db_user_no_password
    else:
        
        # Create full user data with defaults
        userData = UserPydantic(
            email=signupData.email,
            password=get_password_hash(signupData.password),
            firstName=signupData.firstName,
            lastName=signupData.lastName,
            monashId=signupData.monashId,
            role=Role.Student,
            faculty=Faculty.Engineering,
            authcate="local",
            monashObjectId=None
        )
        
        return create_user(db, userData)


def get_users(db: Session):
    return db.query(User).all()


def update_user(db: Session, userData: UserPydantic, email: str):
    db_user = db.query(User).filter(User.email == email).all()
    if len(db_user) == 1:
        for field, value in userData.model_dump().items():
            if isinstance(getattr(User, field).type, Enum):
                value = getattr(User, field).type(value)
            setattr(db_user[0], field, value)

        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        return None


def delete_user(db: Session, email: str):
    db_user = db.query(User).filter(User.email == email).all()
    if len(db_user) == 1:
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


