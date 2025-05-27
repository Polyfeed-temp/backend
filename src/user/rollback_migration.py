#!/usr/bin/env python3
"""
User Data Encryption Rollback Script

This script safely rolls back the encryption implementation by:
1. Decrypting all encrypted user data
2. Restoring original unencrypted format
3. Handling foreign key constraints properly
4. Creating backup before rollback

Usage:
    python rollback_migration.py create-backup
    python rollback_migration.py rollback-encryption
    python rollback_migration.py verify-rollback
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database import get_db
from src.user.encryption import get_encryption, decrypt_field
from sqlalchemy import text
from sqlalchemy.orm import Session


class EncryptionRollback:
    """Handles safe rollback of user data encryption."""
    
    def __init__(self, db: Session):
        self.db = db
        self.encryption = get_encryption()
        
        # Tables that reference USER.email
        self.dependent_tables = [
            'FEEDBACK',
            'LOG', 
            'ENROLLMENT'
        ]
        
        # Fields that were encrypted
        self.encrypted_fields = ['email', 'firstName', 'lastName', 'monashId', 'monashObjectId']
    
    def _disable_foreign_key_checks(self):
        """Temporarily disable foreign key checks."""
        print("Disabling foreign key checks...")
        self.db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        self.db.commit()
    
    def _enable_foreign_key_checks(self):
        """Re-enable foreign key checks."""
        print("Re-enabling foreign key checks...")
        self.db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        self.db.commit()
    
    def create_backup(self) -> str:
        """Create a backup of current encrypted data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"user_data_backup_{timestamp}.json"
        
        print(f"Creating backup: {backup_file}")
        
        # Get all user data
        users = self.db.execute(text("""
            SELECT email, password, monashId, monashObjectId, authcate, 
                   lastName, firstName, role, faculty, rowStatus, createdAt, updatedAt
            FROM USER
        """)).fetchall()
        
        backup_data = {
            'timestamp': timestamp,
            'total_users': len(users),
            'users': []
        }
        
        for user in users:
            user_data = {
                'email': user[0],
                'password': user[1],
                'monashId': user[2],
                'monashObjectId': user[3],
                'authcate': user[4],
                'lastName': user[5],
                'firstName': user[6],
                'role': user[7],
                'faculty': user[8],
                'rowStatus': user[9],
                'createdAt': str(user[10]) if user[10] else None,
                'updatedAt': str(user[11]) if user[11] else None
            }
            backup_data['users'].append(user_data)
        
        # Save backup
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"✓ Backup created: {backup_file} ({len(users)} users)")
        return backup_file
    
    def _get_email_mappings_for_rollback(self) -> Dict[str, str]:
        """Get mapping of encrypted emails to decrypted emails."""
        print("Building email decryption mappings...")
        
        # Get all users
        result = self.db.execute(text("SELECT email FROM USER")).fetchall()
        
        email_mappings = {}
        for row in result:
            encrypted_email = row[0]
            
            # Check if it's encrypted
            if self.encryption.is_encrypted(encrypted_email):
                decrypted_email = decrypt_field(encrypted_email)
                email_mappings[encrypted_email] = decrypted_email
                print(f"  {encrypted_email[:20]}... -> {decrypted_email}")
            else:
                print(f"  {encrypted_email} already decrypted, skipping")
        
        return email_mappings
    
    def _update_dependent_tables_for_rollback(self, email_mappings: Dict[str, str]):
        """Update foreign key references and other encrypted email fields in dependent tables."""
        print("Updating dependent tables with decrypted emails...")
        
        # Define email fields that need decryption for each table
        table_email_fields = {
            'FEEDBACK': ['studentEmail', 'markerEmail'],
            'LOG': ['userEmail'],
            'ENROLLMENT': ['userEmail'],
            'FEEDBACK_REQUEST': ['student_id'],  # This might be unencrypted already
            'HIGHLIGHT': [],  # No email fields to decrypt
            'ACTION': []  # No email fields to decrypt
        }
        
        for table in self.dependent_tables:
            print(f"  Updating {table}...")
            
            # Get email fields for this table
            email_fields = table_email_fields.get(table, [])
            
            if not email_fields:
                print(f"    No email fields to decrypt in {table}")
                continue
            
            for field in email_fields:
                print(f"    Decrypting {table}.{field}...")
                
                # Get all rows with encrypted emails in this field
                try:
                    rows = self.db.execute(text(f"SELECT id, {field} FROM {table} WHERE {field} IS NOT NULL")).fetchall()
                    
                    updated_count = 0
                    for row in rows:
                        row_id = row[0]
                        encrypted_value = row[1]
                        
                        # Check if this value is encrypted
                        if encrypted_value and self.encryption.is_encrypted(encrypted_value):
                            try:
                                decrypted_value = decrypt_field(encrypted_value)
                                
                                # Update the row with decrypted value
                                update_sql = f"UPDATE {table} SET {field} = :decrypted_value WHERE id = :row_id"
                                self.db.execute(text(update_sql), {
                                    'decrypted_value': decrypted_value,
                                    'row_id': row_id
                                })
                                updated_count += 1
                                
                            except Exception as e:
                                print(f"      Warning: Failed to decrypt {field} for row {row_id}: {e}")
                        
                    if updated_count > 0:
                        print(f"      Decrypted {updated_count} {field} values in {table}")
                    else:
                        print(f"      No encrypted {field} values found in {table}")
                        
                except Exception as e:
                    print(f"      Error processing {table}.{field}: {e}")
    
    def _update_user_table_for_rollback(self, email_mappings: Dict[str, str]):
        """Update the USER table with decrypted data."""
        print("Updating USER table with decrypted data...")
        
        for encrypted_email, decrypted_email in email_mappings.items():
            # Get the user data
            user_result = self.db.execute(text("""
                SELECT email, firstName, lastName, monashId, monashObjectId 
                FROM USER WHERE email = :email
            """), {'email': encrypted_email}).fetchone()
            
            if not user_result:
                continue
            
            # Prepare decrypted data
            decrypted_data = {}
            for i, field in enumerate(['email', 'firstName', 'lastName', 'monashId', 'monashObjectId']):
                value = user_result[i]
                if value and self.encryption.is_encrypted(value):
                    decrypted_data[field] = decrypt_field(value)
                else:
                    decrypted_data[field] = value
            
            # Update the user record
            update_sql = """
                UPDATE USER SET 
                    email = :email,
                    firstName = :firstName,
                    lastName = :lastName,
                    monashId = :monashId,
                    monashObjectId = :monashObjectId
                WHERE email = :old_email
            """
            
            self.db.execute(text(update_sql), {
                **decrypted_data,
                'old_email': encrypted_email
            })
            
            print(f"  Updated user: {decrypted_email}")
    
    def rollback_encryption(self) -> bool:
        """Safely rollback all user data to unencrypted format."""
        try:
            print("Starting rollback to unencrypted format...")
            
            # Step 1: Get email mappings for USER table
            email_mappings = self._get_email_mappings_for_rollback()
            
            # Step 2: Disable foreign key checks
            self._disable_foreign_key_checks()
            
            try:
                # Step 3: Always update dependent tables (they might have encrypted data even if USER table doesn't)
                self._update_dependent_tables_for_rollback(email_mappings)
                
                # Step 4: Update USER table if needed
                if email_mappings:
                    print(f"Found {len(email_mappings)} users to rollback in USER table")
                    self._update_user_table_for_rollback(email_mappings)
                else:
                    print("No encrypted emails found in USER table")
                
                # Step 5: Commit all changes
                self.db.commit()
                print("Rollback completed successfully!")
                
            finally:
                # Step 6: Always re-enable foreign key checks
                self._enable_foreign_key_checks()
            
            return True
            
        except Exception as e:
            print(f"Rollback failed: {e}")
            self.db.rollback()
            self._enable_foreign_key_checks()
            return False
    
    def verify_rollback(self) -> bool:
        """Verify that rollback was successful."""
        print("Verifying rollback...")
        
        try:
            encrypted_count = 0
            
            # Check USER table fields
            print("  Checking USER table...")
            result = self.db.execute(text("SELECT email, firstName, lastName, monashId FROM USER LIMIT 10")).fetchall()
            
            for row in result:
                for i, field in enumerate(['email', 'firstName', 'lastName', 'monashId']):
                    value = row[i]
                    if value and self.encryption.is_encrypted(value):
                        print(f"    ✗ USER.{field} still encrypted: {value[:20]}...")
                        encrypted_count += 1
            
            # Check dependent tables
            table_email_fields = {
                'FEEDBACK': ['studentEmail', 'markerEmail'],
                'LOG': ['userEmail'],
                'ENROLLMENT': ['userEmail'],
                'FEEDBACK_REQUEST': ['student_id']
            }
            
            for table, fields in table_email_fields.items():
                print(f"  Checking {table} table...")
                for field in fields:
                    try:
                        result = self.db.execute(text(f"SELECT {field} FROM {table} WHERE {field} IS NOT NULL LIMIT 5")).fetchall()
                        
                        for row in result:
                            value = row[0]
                            if value and self.encryption.is_encrypted(value):
                                print(f"    ✗ {table}.{field} still encrypted: {value[:20]}...")
                                encrypted_count += 1
                                
                    except Exception as e:
                        print(f"    Warning: Could not check {table}.{field}: {e}")
            
            if encrypted_count == 0:
                print("✓ All sampled fields are decrypted")
                print("✓ Rollback verification successful!")
                return True
            else:
                print(f"✗ Found {encrypted_count} encrypted fields - rollback incomplete")
                return False
            
        except Exception as e:
            print(f"✗ Verification failed: {e}")
            return False


def create_backup():
    """Create a backup of current data."""
    try:
        db = next(get_db())
        rollback = EncryptionRollback(db)
        
        backup_file = rollback.create_backup()
        print(f"\n✅ Backup created successfully: {backup_file}")
        print("You can now safely proceed with rollback if needed.")
        return True
        
    except Exception as e:
        print(f"Backup failed: {e}")
        return False


def rollback_encryption():
    """Rollback the encryption implementation."""
    try:
        db = next(get_db())
        rollback = EncryptionRollback(db)
        
        if rollback.rollback_encryption():
            if rollback.verify_rollback():
                print("\n🎉 Rollback completed and verified successfully!")
                print("\n⚠️  IMPORTANT: Remember to:")
                print("   1. Remove USER_ENCRYPTION_KEY from environment")
                print("   2. Update service.py to remove encryption calls")
                print("   3. Test your application thoroughly")
                return True
            else:
                print("\n❌ Rollback completed but verification failed!")
                return False
        else:
            print("\n❌ Rollback failed!")
            return False
            
    except Exception as e:
        print(f"Rollback error: {e}")
        return False


def verify_rollback():
    """Verify rollback was successful."""
    try:
        db = next(get_db())
        rollback = EncryptionRollback(db)
        
        if rollback.verify_rollback():
            print("\n✅ Rollback verification passed!")
            return True
        else:
            print("\n❌ Rollback verification failed!")
            return False
            
    except Exception as e:
        print(f"Verification error: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python rollback_migration.py create-backup")
        print("  python rollback_migration.py rollback-encryption")
        print("  python rollback_migration.py verify-rollback")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create-backup":
        if create_backup():
            print("Backup completed successfully!")
        else:
            print("Backup failed!")
            sys.exit(1)
    elif command == "rollback-encryption":
        if rollback_encryption():
            print("Rollback completed successfully!")
        else:
            print("Rollback failed!")
            sys.exit(1)
    elif command == "verify-rollback":
        if verify_rollback():
            print("Verification passed!")
        else:
            print("Verification failed!")
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main() 