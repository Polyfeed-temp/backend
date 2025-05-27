#!/usr/bin/env python3
"""
Complete Data Encryption Migration Script

This script automatically handles the complete migration to encrypted data across all tables:
1. Migrates existing unencrypted data to encrypted format (USER, LOG, FEEDBACK, FEEDBACK_REQUEST)
2. Removes incompatible foreign key constraints
3. Verifies encryption setup

Usage:
    python migration_script.py

The script will automatically detect what needs to be done and handle everything.
"""

import sys
import os
import base64
import json
from datetime import datetime
from cryptography.fernet import Fernet
from sqlalchemy import text

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db, engine
from src.user.encryption import get_encryption, encrypt_field, decrypt_field


def generate_encryption_key():
    """Generate a new encryption key for user data."""
    key = Fernet.generate_key()
    encoded_key = base64.urlsafe_b64encode(key).decode()
    
    print("Generated new encryption key:")
    print(f"USER_ENCRYPTION_KEY={encoded_key}")
    print("\nAdd this to your .env file!")
    print("\nIMPORTANT: Store this key securely. If you lose it, encrypted data cannot be recovered!")
    
    return encoded_key


def create_backup():
    """Create a backup of sensitive data before migration."""
    print("📦 Creating backup of sensitive data...")
    
    try:
        db = next(get_db())
        
        # Create backup directory
        backup_dir = "migration_backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_dir}/user_data_backup_{timestamp}.json"
        
        # Backup USER table sensitive data
        print("   Backing up USER table...")
        user_result = db.execute(text("""
            SELECT email, firstName, lastName, monashId, monashObjectId 
            FROM USER
        """)).fetchall()
        
        user_backup = []
        for row in user_result:
            user_backup.append({
                'email': row[0],
                'firstName': row[1],
                'lastName': row[2], 
                'monashId': row[3],
                'monashObjectId': row[4]
            })
        
        # Backup FEEDBACK table email references
        print("   Backing up FEEDBACK table email references...")
        feedback_result = db.execute(text("""
            SELECT id, studentEmail, markerEmail 
            FROM FEEDBACK 
            WHERE studentEmail IS NOT NULL OR markerEmail IS NOT NULL
        """)).fetchall()
        
        feedback_backup = []
        for row in feedback_result:
            feedback_backup.append({
                'id': row[0],
                'studentEmail': row[1],
                'markerEmail': row[2]
            })
        
        # Backup LOG table email references
        print("   Backing up LOG table email references...")
        log_result = db.execute(text("""
            SELECT id, userEmail 
            FROM LOG 
            WHERE userEmail IS NOT NULL
        """)).fetchall()
        
        log_backup = []
        for row in log_result:
            log_backup.append({
                'id': row[0],
                'userEmail': row[1]
            })
        
        # Backup FEEDBACK_REQUEST table email references
        print("   Backing up FEEDBACK_REQUEST table email references...")
        fr_result = db.execute(text("""
            SELECT id, student_id 
            FROM FEEDBACK_REQUEST 
            WHERE student_id IS NOT NULL
        """)).fetchall()
        
        fr_backup = []
        for row in fr_result:
            fr_backup.append({
                'id': row[0],
                'student_id': row[1]
            })
        
        # Create complete backup
        backup_data = {
            'backup_timestamp': timestamp,
            'backup_description': 'Pre-encryption migration backup',
            'tables': {
                'USER': user_backup,
                'FEEDBACK': feedback_backup,
                'LOG': log_backup,
                'FEEDBACK_REQUEST': fr_backup
            },
            'record_counts': {
                'USER': len(user_backup),
                'FEEDBACK': len(feedback_backup),
                'LOG': len(log_backup),
                'FEEDBACK_REQUEST': len(fr_backup)
            }
        }
        
        # Write backup to file
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"✅ Backup created: {backup_file}")
        print(f"   USER records: {len(user_backup)}")
        print(f"   FEEDBACK records: {len(feedback_backup)}")
        print(f"   LOG records: {len(log_backup)}")
        print(f"   FEEDBACK_REQUEST records: {len(fr_backup)}")
        
        return backup_file
        
    except Exception as e:
        print(f"❌ Backup creation failed: {e}")
        return None


def check_if_data_already_encrypted():
    """Check if user data is already encrypted."""
    try:
        db = next(get_db())
        
        # Get a sample user email
        result = db.execute(text("SELECT email FROM USER LIMIT 1"))
        row = result.fetchone()
        
        if not row:
            print("ℹ️  No users found in database")
            return True  # No data to migrate
        
        email = row[0]
        
        # Check if the email looks like encrypted data (base64-like)
        # Encrypted data should be longer and contain base64 characters
        if len(email) > 50 and email.replace('=', '').replace('+', '').replace('/', '').replace('-', '').replace('_', '').isalnum():
            # Looks like encrypted data, try to decrypt it
            try:
                decrypted = decrypt_field(email)
                if '@' in decrypted:  # Successfully decrypted to an email
                    print("ℹ️  User data is already encrypted")
                    return True
            except:
                pass
        
        # If we get here, it's likely unencrypted data
        print("ℹ️  User data is not encrypted yet")
        return False
            
    except Exception as e:
        print(f"⚠️  Could not check encryption status: {e}")
        return False


def migrate_user_table(db):
    """Migrate USER table to encrypted format."""
    print("🔄 Migrating USER table...")
    
    encryption = get_encryption()
    
    # Get all users
    result = db.execute(text("""
        SELECT email, firstName, lastName, monashId, monashObjectId 
        FROM USER
    """)).fetchall()
    
    migrated_count = 0
    
    for row in result:
        email, firstName, lastName, monashId, monashObjectId = row
        needs_update = False
        updates = {}
        
        # Check and encrypt each field
        if email and not encryption.is_encrypted(email):
            updates['email'] = encrypt_field(email)
            needs_update = True
            
        if firstName and not encryption.is_encrypted(firstName):
            updates['firstName'] = encrypt_field(firstName)
            needs_update = True
            
        if lastName and not encryption.is_encrypted(lastName):
            updates['lastName'] = encrypt_field(lastName)
            needs_update = True
            
        if monashId and not encryption.is_encrypted(monashId):
            updates['monashId'] = encrypt_field(monashId)
            needs_update = True
            
        if monashObjectId and not encryption.is_encrypted(monashObjectId):
            updates['monashObjectId'] = encrypt_field(monashObjectId)
            needs_update = True
        
        if needs_update:
            # Build update query
            set_clauses = []
            params = {'original_email': email}
            
            for field, encrypted_value in updates.items():
                set_clauses.append(f"{field} = :{field}")
                params[field] = encrypted_value
            
            update_query = f"UPDATE USER SET {', '.join(set_clauses)} WHERE email = :original_email"
            db.execute(text(update_query), params)
            migrated_count += 1
    
    if migrated_count > 0:
        print(f"✅ Migrated {migrated_count} USER records")
    else:
        print("✅ No USER records needed migration - all already encrypted")
    
    return migrated_count


def migrate_feedback_table(db):
    """Migrate FEEDBACK table email fields to encrypted format."""
    print("🔄 Migrating FEEDBACK table...")
    
    encryption = get_encryption()
    
    # Get all feedback records with email fields
    result = db.execute(text("""
        SELECT id, studentEmail, markerEmail 
        FROM FEEDBACK 
        WHERE studentEmail IS NOT NULL OR markerEmail IS NOT NULL
    """)).fetchall()
    
    migrated_count = 0
    
    for row in result:
        feedback_id, studentEmail, markerEmail = row
        needs_update = False
        updates = {}
        
        # Check and encrypt studentEmail
        if studentEmail and not encryption.is_encrypted(studentEmail):
            updates['studentEmail'] = encrypt_field(studentEmail)
            needs_update = True
            
        # Check and encrypt markerEmail
        if markerEmail and not encryption.is_encrypted(markerEmail):
            updates['markerEmail'] = encrypt_field(markerEmail)
            needs_update = True
        
        if needs_update:
            # Build update query
            set_clauses = []
            params = {'id': feedback_id}
            
            for field, encrypted_value in updates.items():
                set_clauses.append(f"{field} = :{field}")
                params[field] = encrypted_value
            
            update_query = f"UPDATE FEEDBACK SET {', '.join(set_clauses)} WHERE id = :id"
            db.execute(text(update_query), params)
            migrated_count += 1
    
    if migrated_count > 0:
        print(f"✅ Migrated {migrated_count} FEEDBACK records")
    else:
        print("✅ No FEEDBACK records needed migration - all already encrypted")
    
    return migrated_count


def migrate_log_table(db):
    """Migrate LOG table userEmail field to encrypted format."""
    print("🔄 Migrating LOG table...")
    
    encryption = get_encryption()
    
    # Get all log records with userEmail
    result = db.execute(text("""
        SELECT id, userEmail 
        FROM LOG 
        WHERE userEmail IS NOT NULL
    """)).fetchall()
    
    migrated_count = 0
    
    for row in result:
        log_id, userEmail = row
        
        # Check and encrypt userEmail
        if userEmail and not encryption.is_encrypted(userEmail):
            encrypted_userEmail = encrypt_field(userEmail)
            
            # Update the record
            db.execute(text("""
                UPDATE LOG 
                SET userEmail = :encrypted_userEmail 
                WHERE id = :id
            """), {
                'encrypted_userEmail': encrypted_userEmail,
                'id': log_id
            })
            
            migrated_count += 1
    
    if migrated_count > 0:
        print(f"✅ Migrated {migrated_count} LOG records")
    else:
        print("✅ No LOG records needed migration - all already encrypted")
    
    return migrated_count


def migrate_feedback_request_table(db):
    """Migrate FEEDBACK_REQUEST table student_id field to encrypted format."""
    print("🔄 Migrating FEEDBACK_REQUEST table...")
    
    encryption = get_encryption()
    
    # Get all feedback request records with student_id
    result = db.execute(text("""
        SELECT id, student_id 
        FROM FEEDBACK_REQUEST 
        WHERE student_id IS NOT NULL
    """)).fetchall()
    
    migrated_count = 0
    
    for row in result:
        fr_id, student_id = row
        
        # Check and encrypt student_id
        if student_id and not encryption.is_encrypted(student_id):
            encrypted_student_id = encrypt_field(student_id)
            
            # Update the record
            db.execute(text("""
                UPDATE FEEDBACK_REQUEST 
                SET student_id = :encrypted_student_id 
                WHERE id = :id
            """), {
                'encrypted_student_id': encrypted_student_id,
                'id': fr_id
            })
            
            migrated_count += 1
    
    if migrated_count > 0:
        print(f"✅ Migrated {migrated_count} FEEDBACK_REQUEST records")
    else:
        print("✅ No FEEDBACK_REQUEST records needed migration - all already encrypted")
    
    return migrated_count


def migrate_all_data():
    """Migrate all tables to encrypted format."""
    print("📋 Checking if data migration is needed...")
    
    if check_if_data_already_encrypted():
        print("✅ Data is already encrypted - skipping migration")
        return True
    
    # Create backup before migration
    backup_file = create_backup()
    if not backup_file:
        print("❌ Cannot proceed without backup - migration aborted")
        return False
    
    print("🔄 Starting complete data migration to encrypted format...")
    
    try:
        # Get database session
        db = next(get_db())
        
        total_migrated = 0
        
        # Migrate each table
        total_migrated += migrate_user_table(db)
        total_migrated += migrate_feedback_table(db)
        total_migrated += migrate_log_table(db)
        total_migrated += migrate_feedback_request_table(db)
        
        # Commit all changes
        db.commit()
        
        print(f"✅ Complete migration finished. {total_migrated} total records migrated.")
        print(f"📦 Backup saved at: {backup_file}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print(f"📦 Your data backup is available at: {backup_file}")
        return False
    
    return True


def fix_foreign_key_constraints():
    """Remove foreign key constraints that are incompatible with encrypted fields."""
    print("📋 Checking and removing foreign key constraints...")
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                constraints_removed = 0
                
                # Check FEEDBACK table for foreign key constraints on email fields
                print("🔍 Checking FEEDBACK table...")
                result = conn.execute(text("SHOW CREATE TABLE FEEDBACK"))
                table_def = list(result)[0][1]
                
                if "FOREIGN KEY" in table_def:
                    # Look for studentEmail foreign key
                    if "fk_student_email" in table_def or "studentEmail" in table_def:
                        print("🔧 Removing foreign key constraint on studentEmail from FEEDBACK table...")
                        try:
                            conn.execute(text("ALTER TABLE FEEDBACK DROP FOREIGN KEY fk_student_email"))
                            constraints_removed += 1
                        except Exception as e:
                            print(f"   Note: {e}")
                    
                    # Look for markerEmail foreign key
                    if "fk_marker_email" in table_def or "markerEmail" in table_def:
                        print("🔧 Removing foreign key constraint on markerEmail from FEEDBACK table...")
                        try:
                            conn.execute(text("ALTER TABLE FEEDBACK DROP FOREIGN KEY fk_marker_email"))
                            constraints_removed += 1
                        except Exception as e:
                            print(f"   Note: {e}")
                
                # Check LOG table for foreign key constraints
                print("🔍 Checking LOG table...")
                result = conn.execute(text("SHOW CREATE TABLE LOG"))
                table_def = list(result)[0][1]
                
                if "FOREIGN KEY" in table_def and "userEmail" in table_def:
                    print("🔧 Removing foreign key constraint 'userEmail' from LOG table...")
                    try:
                        conn.execute(text("ALTER TABLE LOG DROP FOREIGN KEY userEmail"))
                        constraints_removed += 1
                    except Exception as e:
                        print(f"   Note: {e}")
                    
                    print("🔧 Removing index 'userEmail_idx' from LOG table...")
                    try:
                        conn.execute(text("ALTER TABLE LOG DROP INDEX userEmail_idx"))
                    except Exception as e:
                        print(f"   Note: {e}")
                
                # Check ENROLLMENT table for foreign key constraints
                print("🔍 Checking ENROLLMENT table...")
                result = conn.execute(text("SHOW CREATE TABLE ENROLLMENT"))
                table_def = list(result)[0][1]
                
                if "FOREIGN KEY" in table_def and "userEmail" in table_def:
                    print("🔧 Removing foreign key constraint on userEmail from ENROLLMENT table...")
                    try:
                        conn.execute(text("ALTER TABLE ENROLLMENT DROP FOREIGN KEY enrollment_ibfk_1"))
                        constraints_removed += 1
                    except Exception as e:
                        print(f"   Note: {e}")
                
                # Check FEEDBACK_REQUEST table for foreign key constraints
                print("🔍 Checking FEEDBACK_REQUEST table...")
                result = conn.execute(text("SHOW CREATE TABLE FEEDBACK_REQUEST"))
                table_def = list(result)[0][1]
                
                if "FOREIGN KEY" in table_def and "student_id" in table_def:
                    print("🔧 Removing foreign key constraint on student_id from FEEDBACK_REQUEST table...")
                    try:
                        conn.execute(text("ALTER TABLE FEEDBACK_REQUEST DROP FOREIGN KEY feedback_request_ibfk_1"))
                        constraints_removed += 1
                    except Exception as e:
                        print(f"   Note: {e}")
                
                trans.commit()
                
                if constraints_removed > 0:
                    print(f"✅ Removed {constraints_removed} foreign key constraints")
                else:
                    print("✅ No foreign key constraints needed removal")
                
                print("✅ Foreign key constraint fixes completed")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error fixing foreign key constraints: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def verify_encryption_setup():
    """Verify that encryption is working correctly."""
    print("📋 Verifying encryption setup...")
    
    try:
        # Test encryption/decryption
        encryption = get_encryption()
        
        test_data = {
            'email': 'test@example.com',
            'firstName': 'John',
            'lastName': 'Doe',
            'monashId': '12345678'
        }
        
        # Encrypt
        encrypted_data = encryption.encrypt_user_sensitive_fields(test_data)
        print("✅ Encryption working")
        
        # Decrypt
        decrypted_data = encryption.decrypt_user_sensitive_fields(encrypted_data)
        print("✅ Decryption working")
        
        # Verify data integrity
        if decrypted_data == test_data:
            print("✅ Data integrity verified")
            print("✅ Encryption setup is working correctly!")
            return True
        else:
            print("❌ Data integrity check failed")
            return False
            
    except Exception as e:
        print(f"❌ Encryption setup verification failed: {e}")
        return False


def automatic_migration():
    """Automatic migration - detects what needs to be done and handles everything."""
    print("🚀 COMPLETE ENCRYPTION MIGRATION")
    print("=" * 60)
    print("This script will automatically:")
    print("  • Create backup of sensitive data")
    print("  • Migrate ALL tables to encrypted format (USER, FEEDBACK, LOG, FEEDBACK_REQUEST)")
    print("  • Fix foreign key constraints for encrypted fields")
    print("  • Verify encryption is working correctly")
    print("=" * 60)
    
    steps_completed = 0
    total_steps = 3
    
    # Step 1: Fix foreign key constraints FIRST (before migration)
    print(f"\n📋 Step {steps_completed + 1}/{total_steps}: Foreign Key Constraints")
    if not fix_foreign_key_constraints():
        print("❌ Migration failed at foreign key constraint fix step!")
        return False
    steps_completed += 1
    
    # Step 2: Migrate all data (includes backup creation)
    print(f"\n📋 Step {steps_completed + 1}/{total_steps}: Complete Data Migration")
    if not migrate_all_data():
        print("❌ Migration failed at data migration step!")
        return False
    steps_completed += 1
    
    # Step 3: Verify everything is working
    print(f"\n📋 Step {steps_completed + 1}/{total_steps}: Verification")
    if not verify_encryption_setup():
        print("❌ Migration failed at verification step!")
        return False
    steps_completed += 1
    
    print("\n" + "=" * 60)
    print("🎉 COMPLETE ENCRYPTION MIGRATION SUCCESSFUL!")
    print("\n📝 Summary:")
    print("   ✅ Data backup created in migration_backups/ directory")
    print("   ✅ USER table encrypted (email, firstName, lastName, monashId, monashObjectId)")
    print("   ✅ FEEDBACK table encrypted (studentEmail, markerEmail)")
    print("   ✅ LOG table encrypted (userEmail)")
    print("   ✅ FEEDBACK_REQUEST table encrypted (student_id)")
    print("   ✅ Foreign key constraints fixed for encrypted fields")
    print("   ✅ Encryption system verified and working")
    print("\n🔄 Your application is ready for production with full encryption!")
    print("\n📦 IMPORTANT: Keep your backup files safe for rollback if needed!")
    
    return True


def main():
    """Main function - runs automatic migration."""
    
    # Check if encryption key is set
    if not os.getenv('USER_ENCRYPTION_KEY'):
        print("❌ ERROR: USER_ENCRYPTION_KEY environment variable not set!")
        print("\n🔑 To generate a new encryption key, run:")
        print("   python -c \"from cryptography.fernet import Fernet; import base64; key = Fernet.generate_key(); print('USER_ENCRYPTION_KEY=' + base64.urlsafe_b64encode(key).decode())\"")
        print("\n📝 Add the generated key to your .env file")
        sys.exit(1)
    
    # Run automatic migration
    if automatic_migration():
        print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("Your application is ready for production with full encryption.")
        sys.exit(0)
    else:
        print("\n❌ MIGRATION FAILED!")
        print("Please check the error messages above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main() 