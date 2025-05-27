#!/usr/bin/env python3
"""
Decrypt Rollback Script

This script reverts encrypted data back to unencrypted format.
Use this to test the migration script with backup functionality.

⚠️ WARNING: This will decrypt all encrypted data back to plaintext!
Only use this for testing purposes.

Usage:
    python src/user/decrypt_rollback_script.py
"""

import sys
import os
from sqlalchemy import text

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db, engine
from src.user.encryption import decrypt_field


def decrypt_user_table():
    """Decrypt all encrypted fields in USER table."""
    print("🔓 Decrypting USER table...")
    
    try:
        db = next(get_db())
        
        # Get all users
        result = db.execute(text("""
            SELECT email, firstName, lastName, monashId, monashObjectId 
            FROM USER
        """)).fetchall()
        
        decrypted_count = 0
        
        for row in result:
            email, firstName, lastName, monashId, monashObjectId = row
            
            # Decrypt each field if it's encrypted
            try:
                decrypted_email = decrypt_field(email) if email else email
                decrypted_firstName = decrypt_field(firstName) if firstName else firstName
                decrypted_lastName = decrypt_field(lastName) if lastName else lastName
                decrypted_monashId = decrypt_field(monashId) if monashId else monashId
                decrypted_monashObjectId = decrypt_field(monashObjectId) if monashObjectId else monashObjectId
                
                # Update the record with decrypted data
                db.execute(text("""
                    UPDATE USER SET 
                        email = :new_email,
                        firstName = :new_firstName,
                        lastName = :new_lastName,
                        monashId = :new_monashId,
                        monashObjectId = :new_monashObjectId
                    WHERE email = :old_email
                """), {
                    'new_email': decrypted_email,
                    'new_firstName': decrypted_firstName,
                    'new_lastName': decrypted_lastName,
                    'new_monashId': decrypted_monashId,
                    'new_monashObjectId': decrypted_monashObjectId,
                    'old_email': email
                })
                
                decrypted_count += 1
                print(f"   Decrypted user: {decrypted_email}")
                
            except Exception as e:
                print(f"   Skipping user (already decrypted or error): {str(e)[:50]}...")
        
        db.commit()
        print(f"✅ USER table: {decrypted_count} users decrypted")
        return True
        
    except Exception as e:
        print(f"❌ Error decrypting USER table: {e}")
        return False


def decrypt_feedback_table():
    """Decrypt all encrypted email fields in FEEDBACK table."""
    print("🔓 Decrypting FEEDBACK table...")
    
    try:
        db = next(get_db())
        
        # Get all feedback records with email fields
        result = db.execute(text("""
            SELECT id, studentEmail, markerEmail 
            FROM FEEDBACK 
            WHERE studentEmail IS NOT NULL OR markerEmail IS NOT NULL
        """)).fetchall()
        
        decrypted_count = 0
        
        for row in result:
            feedback_id, studentEmail, markerEmail = row
            
            try:
                # Decrypt email fields if they're encrypted
                decrypted_studentEmail = decrypt_field(studentEmail) if studentEmail else studentEmail
                decrypted_markerEmail = decrypt_field(markerEmail) if markerEmail else markerEmail
                
                # Update the record
                db.execute(text("""
                    UPDATE FEEDBACK SET 
                        studentEmail = :studentEmail,
                        markerEmail = :markerEmail
                    WHERE id = :id
                """), {
                    'studentEmail': decrypted_studentEmail,
                    'markerEmail': decrypted_markerEmail,
                    'id': feedback_id
                })
                
                decrypted_count += 1
                
            except Exception as e:
                print(f"   Skipping feedback {feedback_id} (already decrypted or error): {str(e)[:50]}...")
        
        db.commit()
        print(f"✅ FEEDBACK table: {decrypted_count} records decrypted")
        return True
        
    except Exception as e:
        print(f"❌ Error decrypting FEEDBACK table: {e}")
        return False


def decrypt_log_table():
    """Decrypt all encrypted email fields in LOG table."""
    print("🔓 Decrypting LOG table...")
    
    try:
        db = next(get_db())
        
        # Get all log records with email fields
        result = db.execute(text("""
            SELECT id, userEmail 
            FROM LOG 
            WHERE userEmail IS NOT NULL
        """)).fetchall()
        
        decrypted_count = 0
        
        for row in result:
            log_id, userEmail = row
            
            try:
                # Decrypt email field if it's encrypted
                decrypted_userEmail = decrypt_field(userEmail) if userEmail else userEmail
                
                # Update the record
                db.execute(text("""
                    UPDATE LOG SET userEmail = :userEmail WHERE id = :id
                """), {
                    'userEmail': decrypted_userEmail,
                    'id': log_id
                })
                
                decrypted_count += 1
                
            except Exception as e:
                print(f"   Skipping log {log_id} (already decrypted or error): {str(e)[:50]}...")
        
        db.commit()
        print(f"✅ LOG table: {decrypted_count} records decrypted")
        return True
        
    except Exception as e:
        print(f"❌ Error decrypting LOG table: {e}")
        return False


def decrypt_feedback_request_table():
    """Decrypt all encrypted email fields in FEEDBACK_REQUEST table."""
    print("🔓 Decrypting FEEDBACK_REQUEST table...")
    
    try:
        db = next(get_db())
        
        # Get all feedback request records with email fields
        result = db.execute(text("""
            SELECT id, student_id 
            FROM FEEDBACK_REQUEST 
            WHERE student_id IS NOT NULL
        """)).fetchall()
        
        decrypted_count = 0
        
        for row in result:
            fr_id, student_id = row
            
            try:
                # Decrypt email field if it's encrypted
                decrypted_student_id = decrypt_field(student_id) if student_id else student_id
                
                # Update the record
                db.execute(text("""
                    UPDATE FEEDBACK_REQUEST SET student_id = :student_id WHERE id = :id
                """), {
                    'student_id': decrypted_student_id,
                    'id': fr_id
                })
                
                decrypted_count += 1
                
            except Exception as e:
                print(f"   Skipping feedback_request {fr_id} (already decrypted or error): {str(e)[:50]}...")
        
        db.commit()
        print(f"✅ FEEDBACK_REQUEST table: {decrypted_count} records decrypted")
        return True
        
    except Exception as e:
        print(f"❌ Error decrypting FEEDBACK_REQUEST table: {e}")
        return False


def restore_log_foreign_key_constraint():
    """Restore the foreign key constraint on LOG table."""
    print("🔧 Restoring LOG table foreign key constraint...")
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # Check if constraint already exists
                result = conn.execute(text("SHOW CREATE TABLE LOG"))
                table_def = list(result)[0][1]
                
                if "FOREIGN KEY" in table_def and "userEmail" in table_def:
                    print("✅ LOG table foreign key constraint already exists")
                else:
                    # Add the foreign key constraint back
                    print("   Adding foreign key constraint...")
                    conn.execute(text("""
                        ALTER TABLE LOG 
                        ADD CONSTRAINT userEmail 
                        FOREIGN KEY (userEmail) REFERENCES USER (email) 
                        ON DELETE NO ACTION ON UPDATE NO ACTION
                    """))
                    
                    # Add index back
                    print("   Adding index...")
                    conn.execute(text("ALTER TABLE LOG ADD INDEX userEmail_idx (userEmail)"))
                    
                    print("✅ LOG table foreign key constraint restored")
                
                trans.commit()
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error restoring foreign key constraint: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def main():
    print("🔓 DECRYPT ROLLBACK SCRIPT")
    print("=" * 50)
    print("⚠️  WARNING: This will decrypt all encrypted data back to plaintext!")
    print("This is intended for testing the migration script with backup functionality.")
    print("=" * 50)
    
    # Ask for confirmation
    response = input("\nAre you sure you want to decrypt all data? (yes/no): ")
    if response.lower() != 'yes':
        print("Decrypt rollback cancelled")
        sys.exit(0)
    
    print("\n🚀 Starting decrypt rollback...")
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Decrypt USER table
    if decrypt_user_table():
        success_count += 1
    
    # Step 2: Decrypt FEEDBACK table
    if decrypt_feedback_table():
        success_count += 1
    
    # Step 3: Decrypt LOG table
    if decrypt_log_table():
        success_count += 1
    
    # Step 4: Decrypt FEEDBACK_REQUEST table
    if decrypt_feedback_request_table():
        success_count += 1
    
    # Step 5: Restore foreign key constraint
    if restore_log_foreign_key_constraint():
        success_count += 1
    
    print("\n" + "=" * 50)
    if success_count == total_steps:
        print("🎉 DECRYPT ROLLBACK COMPLETED SUCCESSFULLY!")
        print("\n📝 Summary:")
        print("   ✅ All encrypted data reverted to plaintext")
        print("   ✅ Foreign key constraints restored")
        print("\n🧪 You can now test the migration script with backup functionality:")
        print("   python src/user/migration_script.py")
    else:
        print(f"⚠️  DECRYPT ROLLBACK PARTIALLY COMPLETED ({success_count}/{total_steps} steps)")
        print("Some steps may have failed. Check the error messages above.")
    
    print("\n⚠️  Remember to restart your application after rollback!")


if __name__ == "__main__":
    main() 