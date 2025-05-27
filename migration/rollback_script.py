#!/usr/bin/env python3
"""
Rollback Script for Encryption Migration

This script can restore data from backups created by the migration script.

Usage:
    python src/user/rollback_script.py [backup_file]
    
If no backup file is specified, it will list available backups.
"""

import sys
import os
import json
from sqlalchemy import text

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db, engine


def list_available_backups():
    """List all available backup files."""
    backup_dir = "migration_backups"
    
    if not os.path.exists(backup_dir):
        print("❌ No backup directory found")
        return []
    
    backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
    
    if not backup_files:
        print("❌ No backup files found")
        return []
    
    print("📦 Available backup files:")
    for i, backup_file in enumerate(sorted(backup_files), 1):
        backup_path = os.path.join(backup_dir, backup_file)
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            timestamp = backup_data.get('backup_timestamp', 'Unknown')
            record_counts = backup_data.get('record_counts', {})
            
            print(f"  {i}. {backup_file}")
            print(f"     Created: {timestamp}")
            print(f"     Records: USER({record_counts.get('USER', 0)}), "
                  f"FEEDBACK({record_counts.get('FEEDBACK', 0)}), "
                  f"LOG({record_counts.get('LOG', 0)}), "
                  f"FEEDBACK_REQUEST({record_counts.get('FEEDBACK_REQUEST', 0)})")
            
        except Exception as e:
            print(f"  {i}. {backup_file} (Error reading: {e})")
    
    return [os.path.join(backup_dir, f) for f in sorted(backup_files)]


def restore_from_backup(backup_file):
    """Restore data from a backup file."""
    print(f"🔄 Restoring data from backup: {backup_file}")
    
    try:
        # Load backup data
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        print(f"   Backup created: {backup_data.get('backup_timestamp')}")
        print(f"   Description: {backup_data.get('backup_description')}")
        
        db = next(get_db())
        
        # Disable foreign key checks for safe restoration
        print("   Disabling foreign key checks...")
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        db.commit()
        
        try:
            # Restore USER table
            user_data = backup_data['tables']['USER']
            print(f"   Restoring {len(user_data)} USER records...")
            
            for user in user_data:
                db.execute(text("""
                    UPDATE USER SET 
                        email = :email,
                        firstName = :firstName,
                        lastName = :lastName,
                        monashId = :monashId,
                        monashObjectId = :monashObjectId
                    WHERE email = :email OR 
                          firstName = :firstName OR 
                          lastName = :lastName
                """), user)
            
            # Restore FEEDBACK table
            feedback_data = backup_data['tables']['FEEDBACK']
            print(f"   Restoring {len(feedback_data)} FEEDBACK records...")
            
            for feedback in feedback_data:
                db.execute(text("""
                    UPDATE FEEDBACK SET 
                        studentEmail = :studentEmail,
                        markerEmail = :markerEmail
                    WHERE id = :id
                """), feedback)
            
            # Restore LOG table
            log_data = backup_data['tables']['LOG']
            print(f"   Restoring {len(log_data)} LOG records...")
            
            for log in log_data:
                db.execute(text("""
                    UPDATE LOG SET userEmail = :userEmail WHERE id = :id
                """), log)
            
            # Restore FEEDBACK_REQUEST table
            fr_data = backup_data['tables']['FEEDBACK_REQUEST']
            print(f"   Restoring {len(fr_data)} FEEDBACK_REQUEST records...")
            
            for fr in fr_data:
                db.execute(text("""
                    UPDATE FEEDBACK_REQUEST SET student_id = :student_id WHERE id = :id
                """), fr)
            
            # Commit all changes
            db.commit()
            print("✅ Data restoration completed successfully")
            
        finally:
            # Re-enable foreign key checks
            print("   Re-enabling foreign key checks...")
            db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            db.commit()
        
        print("🎉 Rollback completed successfully!")
        print("⚠️  Remember to restart your application after rollback")
        
        return True
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False


def main():
    print("🔄 ENCRYPTION MIGRATION ROLLBACK TOOL")
    print("=" * 50)
    
    if len(sys.argv) == 1:
        # No backup file specified, list available backups
        backup_files = list_available_backups()
        
        if not backup_files:
            print("\n❌ No backups available for rollback")
            sys.exit(1)
        
        print(f"\nUsage: python {sys.argv[0]} <backup_file>")
        print("Example:")
        if backup_files:
            print(f"  python {sys.argv[0]} {backup_files[0]}")
        
        sys.exit(0)
    
    backup_file = sys.argv[1]
    
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        sys.exit(1)
    
    print(f"⚠️  WARNING: This will restore data from backup and overwrite current encrypted data!")
    print(f"Backup file: {backup_file}")
    
    # Ask for confirmation
    response = input("\nAre you sure you want to proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Rollback cancelled")
        sys.exit(0)
    
    if restore_from_backup(backup_file):
        print("\n✅ Rollback completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Rollback failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 