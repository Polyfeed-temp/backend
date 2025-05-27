from sqlalchemy.orm import Session
from .models import Enrollment
from .schemas import EnrollmentPydantic
from src.user.encryption import encrypt_field, decrypt_field


# Function to create a student unit
def create_student_unit(db: Session, student_unit: EnrollmentPydantic):
    enrollment_data = student_unit.model_dump()
    
    # Encrypt userEmail before storage
    if 'userEmail' in enrollment_data and enrollment_data['userEmail']:
        enrollment_data['userEmail'] = encrypt_field(enrollment_data['userEmail'])
    
    db_student_unit = Enrollment(**enrollment_data)
    db.add(db_student_unit)
    db.commit()
    db.refresh(db_student_unit)
    
    # Return decrypted data for response
    response_data = student_unit.model_dump()  # Use original unencrypted data
    response_data['id'] = db_student_unit.id
    return response_data


# Function to read a student unit by ID
def get_student_unit_by_id(db: Session, student_unit_id: int):
    return db.query(Enrollment).filter(Enrollment.id == student_unit_id).first()


# Function to get all student units
def get_all_student_units(db: Session):
    enrollments = db.query(Enrollment).all()
    
    # Decrypt userEmail fields for response
    decrypted_enrollments = []
    for enrollment in enrollments:
        enrollment_dict = {
            'id': enrollment.id,
            'unitCode': enrollment.unitCode
        }
        
        # Decrypt userEmail
        if enrollment.userEmail:
            try:
                enrollment_dict['userEmail'] = decrypt_field(enrollment.userEmail)
            except:
                enrollment_dict['userEmail'] = enrollment.userEmail  # If decryption fails, keep original
        else:
            enrollment_dict['userEmail'] = enrollment.userEmail
            
        decrypted_enrollments.append(enrollment_dict)
    
    return decrypted_enrollments


# Function to update a student unit
def update_student_unit(db: Session, student_unit_id: int, updated_student_unit: EnrollmentPydantic):
    db.query(Enrollment).filter(Enrollment.id == student_unit_id).update(updated_student_unit.dict())
    db.commit()
    return updated_student_unit


# Function to delete a student unit
def delete_student_unit(db: Session, student_unit_id: int):
    student_unit = db.query(Enrollment).filter(Enrollment.id == student_unit_id).first()
    if student_unit:
        db.delete(student_unit)
        db.commit()
        return True
    else:
        return False


def get_student_all_units(db: Session, studentId: int):
    return db.query(Enrollment).filter(Enrollment.studentId == studentId).all()


def get_students_by_unit(db: Session, unitCode: str):
    enrollments = db.query(Enrollment).filter(Enrollment.unitCode == unitCode).all()
    
    # Decrypt userEmail fields for response
    decrypted_enrollments = []
    for enrollment in enrollments:
        enrollment_dict = {
            'id': enrollment.id,
            'unitCode': enrollment.unitCode
        }
        
        # Decrypt userEmail
        if enrollment.userEmail:
            try:
                enrollment_dict['userEmail'] = decrypt_field(enrollment.userEmail)
            except:
                enrollment_dict['userEmail'] = enrollment.userEmail  # If decryption fails, keep original
        else:
            enrollment_dict['userEmail'] = enrollment.userEmail
            
        decrypted_enrollments.append(enrollment_dict)
    
    return decrypted_enrollments


def get_enrollments_by_user_email(db: Session, user_email: str):
    """Get enrollments for a specific user by searching through encrypted emails."""
    all_enrollments = db.query(Enrollment).all()
    user_enrollments = []
    
    for enrollment in all_enrollments:
        if enrollment.userEmail:
            try:
                decrypted_email = decrypt_field(enrollment.userEmail)
                if decrypted_email == user_email:
                    enrollment_dict = {
                        'id': enrollment.id,
                        'userEmail': decrypted_email,
                        'unitCode': enrollment.unitCode
                    }
                    user_enrollments.append(enrollment_dict)
            except:
                # If decryption fails, check if it's already unencrypted
                if enrollment.userEmail == user_email:
                    enrollment_dict = {
                        'id': enrollment.id,
                        'userEmail': enrollment.userEmail,
                        'unitCode': enrollment.unitCode
                    }
                    user_enrollments.append(enrollment_dict)
    
    return user_enrollments
