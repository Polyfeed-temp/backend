#!/usr/bin/env python3
"""
Feedback and Feedback Request Encryption Migration Script

This script migrates existing unencrypted email data in FEEDBACK and FEEDBACK_REQUEST tables
to encrypted format.

Usage:
    python migrate_feedback_encryption.py migrate-feedback
    python migrate_feedback_encryption.py migrate-feedback-request
    python migrate_feedback_encryption.py migrate-all
    python migrate_feedback_encryption.py verify-migration
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database import get_db
from src.user.encryption import get_encryption, encrypt_field
from sqlalchemy import text
from sqlalchemy.orm import Session


class FeedbackEncryptionMigration:
    """Handles migration of feedback and feedback_request email data to encrypted format."""
    
    def __init__(self, db: Session):
        self.db = db
        self.encryption = get_encryption()
    
    def migrate_feedback_table(self) -> bool:
        """Migrate FEEDBACK table email fields to encrypted format."""
        try:
            print("Starting FEEDBACK table migration...")
            
            # Disable foreign key checks temporarily
            print("  Disabling foreign key checks...")
            self.db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            self.db.commit()
            
            # Get all feedback records
            result = self.db.execute(text("""
                SELECT id, studentEmail, markerEmail 
                FROM FEEDBACK 
                WHERE studentEmail IS NOT NULL OR markerEmail IS NOT NULL
            """)).fetchall()
            
            migrated_count = 0
            
            for row in result:
                feedback_id = row[0]
                student_email = row[1]
                marker_email = row[2]
                
                needs_update = False
                update_data = {}
                
                # Check and encrypt studentEmail
                if student_email and not self.encryption.is_encrypted(student_email):
                    encrypted_student_email = encrypt_field(student_email)
                    update_data['studentEmail'] = encrypted_student_email
                    needs_update = True
                    print(f"  Encrypting studentEmail: {student_email} -> {encrypted_student_email[:30]}...")
                
                # Check and encrypt markerEmail
                if marker_email and not self.encryption.is_encrypted(marker_email):
                    encrypted_marker_email = encrypt_field(marker_email)
                    update_data['markerEmail'] = encrypted_marker_email
                    needs_update = True
                    print(f"  Encrypting markerEmail: {marker_email} -> {encrypted_marker_email[:30]}...")
                
                # Update the record if needed
                if needs_update:
                    update_sql = "UPDATE FEEDBACK SET "
                    update_parts = []
                    
                    if 'studentEmail' in update_data:
                        update_parts.append("studentEmail = :studentEmail")
                    if 'markerEmail' in update_data:
                        update_parts.append("markerEmail = :markerEmail")
                    
                    update_sql += ", ".join(update_parts) + " WHERE id = :id"
                    update_data['id'] = feedback_id
                    
                    self.db.execute(text(update_sql), update_data)
                    migrated_count += 1
            
            if migrated_count > 0:
                self.db.commit()
                print(f"✓ Migrated {migrated_count} FEEDBACK records")
            else:
                print("✓ No FEEDBACK records needed migration - all already encrypted")
            
            # Re-enable foreign key checks
            print("  Re-enabling foreign key checks...")
            self.db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            self.db.commit()
            
            return True
            
        except Exception as e:
            print(f"✗ FEEDBACK migration failed: {e}")
            self.db.rollback()
            # Re-enable foreign key checks even on failure
            try:
                self.db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                self.db.commit()
            except:
                pass
            return False
    
    def migrate_feedback_request_table(self) -> bool:
        """Migrate FEEDBACK_REQUEST table email fields to encrypted format."""
        try:
            print("Starting FEEDBACK_REQUEST table migration...")
            
            # Get all feedback request records
            result = self.db.execute(text("""
                SELECT id, student_id 
                FROM FEEDBACK_REQUEST 
                WHERE student_id IS NOT NULL
            """)).fetchall()
            
            migrated_count = 0
            
            for row in result:
                request_id = row[0]
                student_id = row[1]
                
                # Check and encrypt student_id
                if student_id and not self.encryption.is_encrypted(student_id):
                    encrypted_student_id = encrypt_field(student_id)
                    
                    print(f"  Encrypting student_id: {student_id} -> {encrypted_student_id[:30]}...")
                    
                    # Update the record
                    self.db.execute(text("""
                        UPDATE FEEDBACK_REQUEST 
                        SET student_id = :encrypted_student_id 
                        WHERE id = :id
                    """), {
                        'encrypted_student_id': encrypted_student_id,
                        'id': request_id
                    })
                    
                    migrated_count += 1
            
            if migrated_count > 0:
                self.db.commit()
                print(f"✓ Migrated {migrated_count} FEEDBACK_REQUEST records")
            else:
                print("✓ No FEEDBACK_REQUEST records needed migration - all already encrypted")
            
            return True
            
        except Exception as e:
            print(f"✗ FEEDBACK_REQUEST migration failed: {e}")
            self.db.rollback()
            return False
    
    def verify_migration(self) -> bool:
        """Verify that migration was successful."""
        print("Verifying migration...")
        
        try:
            unencrypted_count = 0
            
            # Check FEEDBACK table
            print("  Checking FEEDBACK table...")
            result = self.db.execute(text("""
                SELECT studentEmail, markerEmail 
                FROM FEEDBACK 
                WHERE studentEmail IS NOT NULL OR markerEmail IS NOT NULL 
                LIMIT 10
            """)).fetchall()
            
            for row in result:
                student_email = row[0]
                marker_email = row[1]
                
                if student_email and not self.encryption.is_encrypted(student_email):
                    print(f"    ✗ Unencrypted studentEmail: {student_email}")
                    unencrypted_count += 1
                
                if marker_email and not self.encryption.is_encrypted(marker_email):
                    print(f"    ✗ Unencrypted markerEmail: {marker_email}")
                    unencrypted_count += 1
            
            # Check FEEDBACK_REQUEST table
            print("  Checking FEEDBACK_REQUEST table...")
            result = self.db.execute(text("""
                SELECT student_id 
                FROM FEEDBACK_REQUEST 
                WHERE student_id IS NOT NULL 
                LIMIT 10
            """)).fetchall()
            
            for row in result:
                student_id = row[0]
                
                if student_id and not self.encryption.is_encrypted(student_id):
                    print(f"    ✗ Unencrypted student_id: {student_id}")
                    unencrypted_count += 1
            
            if unencrypted_count == 0:
                print("✓ All sampled fields are encrypted")
                print("✓ Migration verification successful!")
                return True
            else:
                print(f"✗ Found {unencrypted_count} unencrypted fields - migration incomplete")
                return False
            
        except Exception as e:
            print(f"✗ Verification failed: {e}")
            return False


def migrate_feedback():
    """Migrate FEEDBACK table."""
    try:
        db = next(get_db())
        migration = FeedbackEncryptionMigration(db)
        
        if migration.migrate_feedback_table():
            print("\n✅ FEEDBACK table migration completed successfully!")
            return True
        else:
            print("\n❌ FEEDBACK table migration failed!")
            return False
            
    except Exception as e:
        print(f"Migration error: {e}")
        return False


def migrate_feedback_request():
    """Migrate FEEDBACK_REQUEST table."""
    try:
        db = next(get_db())
        migration = FeedbackEncryptionMigration(db)
        
        if migration.migrate_feedback_request_table():
            print("\n✅ FEEDBACK_REQUEST table migration completed successfully!")
            return True
        else:
            print("\n❌ FEEDBACK_REQUEST table migration failed!")
            return False
            
    except Exception as e:
        print(f"Migration error: {e}")
        return False


def migrate_all():
    """Migrate both FEEDBACK and FEEDBACK_REQUEST tables."""
    try:
        db = next(get_db())
        migration = FeedbackEncryptionMigration(db)
        
        feedback_success = migration.migrate_feedback_table()
        feedback_request_success = migration.migrate_feedback_request_table()
        
        if feedback_success and feedback_request_success:
            print("\n🎉 All migrations completed successfully!")
            print("\n⚠️  IMPORTANT: Remember to restart your application!")
            return True
        else:
            print("\n❌ Some migrations failed!")
            return False
            
    except Exception as e:
        print(f"Migration error: {e}")
        return False


def verify_migration():
    """Verify migration was successful."""
    try:
        db = next(get_db())
        migration = FeedbackEncryptionMigration(db)
        
        if migration.verify_migration():
            print("\n✅ Migration verification passed!")
            return True
        else:
            print("\n❌ Migration verification failed!")
            return False
            
    except Exception as e:
        print(f"Verification error: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python migrate_feedback_encryption.py migrate-feedback")
        print("  python migrate_feedback_encryption.py migrate-feedback-request")
        print("  python migrate_feedback_encryption.py migrate-all")
        print("  python migrate_feedback_encryption.py verify-migration")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "migrate-feedback":
        if migrate_feedback():
            print("FEEDBACK migration completed successfully!")
        else:
            print("FEEDBACK migration failed!")
            sys.exit(1)
    elif command == "migrate-feedback-request":
        if migrate_feedback_request():
            print("FEEDBACK_REQUEST migration completed successfully!")
        else:
            print("FEEDBACK_REQUEST migration failed!")
            sys.exit(1)
    elif command == "migrate-all":
        if migrate_all():
            print("All migrations completed successfully!")
        else:
            print("Migrations failed!")
            sys.exit(1)
    elif command == "verify-migration":
        if verify_migration():
            print("Verification passed!")
        else:
            print("Verification failed!")
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main() 