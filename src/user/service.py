from enum import Enum

from sqlalchemy.orm import Session
from .models import User
from .schemas import UserPydantic
from src.dependencies import get_password_hash
from src.unit.models import Unit
from src.assessment.models import Assessment
from src.enrollment.models import Enrollment
from .encryption import encrypt_sensitive_data, decrypt_sensitive_data, encrypt_field, decrypt_field


def _prepare_user_data_for_storage(user_data: dict) -> dict:
    """Encrypt sensitive fields before storing to database."""
    return encrypt_sensitive_data(user_data)


def _prepare_user_data_for_response(user_data) -> dict:
    """Decrypt sensitive fields when retrieving from database."""
    if hasattr(user_data, '__dict__'):
        # Convert SQLAlchemy object to dict
        data_dict = {column.name: getattr(user_data, column.name) for column in user_data.__table__.columns}
    elif hasattr(user_data, '_asdict'):
        # SQLAlchemy Row object
        data_dict = user_data._asdict()
    elif hasattr(user_data, 'keys'):
        # Dict-like object
        data_dict = dict(user_data)
    else:
        # Convert to dict manually
        data_dict = {}
        for key in dir(user_data):
            if not key.startswith('_'):
                try:
                    data_dict[key] = getattr(user_data, key)
                except:
                    pass
    
    return decrypt_sensitive_data(data_dict)


def get_user_by_email(db: Session, email: str, no_password: bool = True):
    """
    Get user by email. Since Fernet encryption generates different ciphertext each time,
    we need to decrypt all emails and search for a match.
    """
    # Get all users and decrypt their emails to find a match
    if no_password:
        users = db.query(User).with_entities(
            User.email, User.role, User.faculty, User.monashId, 
            User.monashObjectId, User.authcate, User.lastName, User.firstName
        ).all()
    else:
        users = db.query(User).all()
    
    # Search through users by decrypting emails
    for user in users:
        decrypted_email = decrypt_field(user.email)
        if decrypted_email == email:
            # Found the user, return decrypted data
            return _prepare_user_data_for_response(user)
    
    return None


def create_user(db: Session, userData: UserPydantic):
    # Convert Pydantic model to dict and handle enums
    user_dict = userData.model_dump()
    user_dict['role'] = userData.role.value
    user_dict['faculty'] = userData.faculty.value
    user_dict['monashObjectId'] = None
    
    # Encrypt sensitive fields before storage
    encrypted_user_data = _prepare_user_data_for_storage(user_dict)
    
    db_user = User(**encrypted_user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Return decrypted data for response
    return _prepare_user_data_for_response(db_user)


def signup_user(db: Session, userData: UserPydantic):
    # Check if user already exists by searching through decrypted emails
    existing_user = get_user_by_email(db, userData.email, no_password=False)
    
    if existing_user:
        return False
    else:
        # Hash the password and prepare user data
        user_dict = userData.model_dump()
        user_dict['password'] = get_password_hash(userData.password)
        user_dict['role'] = userData.role.value
        user_dict['faculty'] = userData.faculty.value
        user_dict['monashObjectId'] = None
        
        # Encrypt sensitive fields before storage
        encrypted_user_data = _prepare_user_data_for_storage(user_dict)
        
        db_user = User(**encrypted_user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Return decrypted data for response
        return _prepare_user_data_for_response(db_user)


def get_users(db: Session):
    users = db.query(User).all()
    # Decrypt sensitive fields for all users
    return [_prepare_user_data_for_response(user) for user in users]


def update_user(db: Session, userData: UserPydantic, email: str):
    # Find user by decrypting emails
    users = db.query(User).all()
    target_user = None
    
    for user in users:
        decrypted_email = decrypt_field(user.email)
        if decrypted_email == email:
            target_user = user
            break
    
    if target_user:
        # Prepare update data with encryption
        update_data = userData.model_dump()
        encrypted_update_data = _prepare_user_data_for_storage(update_data)
        
        for field, value in encrypted_update_data.items():
            if hasattr(target_user, field):
                # Handle enum fields
                if isinstance(getattr(User, field).type, Enum):
                    value = getattr(User, field).type(value)
                setattr(target_user, field, value)

        db.commit()
        db.refresh(target_user)
        
        # Return decrypted data for response
        return _prepare_user_data_for_response(target_user)
    else:
        return None


def delete_user(db: Session, email: str):
    # Find user by decrypting emails
    users = db.query(User).all()
    target_user = None
    
    for user in users:
        decrypted_email = decrypt_field(user.email)
        if decrypted_email == email:
            target_user = user
            break
    
    if target_user:
        db.delete(target_user)
        db.commit()
        return True
    else:
        return False


def get_student_all_student_enrolled_units(db: Session, student_email: str):
    """
    Get enrolled units for a student. Since emails are encrypted, we need to
    find the encrypted email first, then use it for the JOIN query.
    """
    # Find the user's encrypted email
    users = db.query(User).all()
    encrypted_email = None
    
    for user in users:
        decrypted_email = decrypt_field(user.email)
        if decrypted_email == student_email:
            encrypted_email = user.email
            break
    
    if not encrypted_email:
        return []
    
    # Fetch the rows using the encrypted email
    results = db.query(
        Unit.unitCode,
        Assessment.assessmentName,
        Assessment.id
    ).join(
        Enrollment, Enrollment.unitCode == Unit.unitCode
    ).join(
        Assessment, Unit.unitCode == Assessment.unitCode
    ).filter(
        Enrollment.userEmail == encrypted_email
    ).all()

    # Process the results
    units = {}
    for unitCode, assessmentName, assessmentId in results:
        if unitCode not in units:
            units[unitCode] = {'unitCode': unitCode, 'assessments': []}
        units[unitCode]['assessments'].append({'assessmentName': assessmentName, 'id': assessmentId})

    return list(units.values())


# Additional utility functions for encryption management

def migrate_existing_data_to_encrypted(db: Session):
    """
    Utility function to migrate existing unencrypted data to encrypted format.
    Should be run once during deployment of encryption feature.
    """
    from .encryption import get_encryption
    
    encryption = get_encryption()
    users = db.query(User).all()
    
    migrated_count = 0
    for user in users:
        needs_migration = False
        
        # Check if data is already encrypted
        sensitive_fields = ['email', 'firstName', 'lastName', 'monashId', 'monashObjectId']
        for field in sensitive_fields:
            value = getattr(user, field, None)
            if value and not encryption.is_encrypted(value):
                # Encrypt the field
                encrypted_value = encrypt_field(value)
                setattr(user, field, encrypted_value)
                needs_migration = True
        
        if needs_migration:
            migrated_count += 1
    
    if migrated_count > 0:
        db.commit()
        print(f"Migrated {migrated_count} users to encrypted format")
    else:
        print("No users needed migration - all data already encrypted")
    
    return migrated_count


