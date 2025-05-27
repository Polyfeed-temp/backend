#!/usr/bin/env python3
import os
os.environ['USER_ENCRYPTION_KEY'] = 'dkdpYkkzRU9QMnJIaG9xMHltNWZMTTUtWXRtbUxpc0J4aEIwcWRjS3ROcz0='

from src.database import get_db
from src.user.encryption import decrypt_field, get_encryption
from sqlalchemy import text

def check_email_fields():
    db = next(get_db())
    encryption = get_encryption()
    
    print("=== FEEDBACK TABLE EMAIL FIELDS ===")
    result = db.execute(text('DESCRIBE FEEDBACK')).fetchall()
    email_fields = []
    for row in result:
        if 'email' in row[0].lower():
            email_fields.append(row[0])
            print(f'  {row[0]} - {row[1]}')
    
    # Check sample data
    if email_fields:
        print("\n--- Sample FEEDBACK data ---")
        for field in email_fields:
            try:
                sample = db.execute(text(f'SELECT {field} FROM FEEDBACK WHERE {field} IS NOT NULL LIMIT 3')).fetchall()
                print(f'\n{field} samples:')
                for row in sample:
                    value = row[0]
                    is_encrypted = encryption.is_encrypted(value) if value else False
                    print(f'  {value[:30]}... (encrypted: {is_encrypted})')
            except Exception as e:
                print(f'  Error checking {field}: {e}')
    
    print("\n=== FEEDBACK_REQUEST TABLE EMAIL FIELDS ===")
    result = db.execute(text('DESCRIBE FEEDBACK_REQUEST')).fetchall()
    email_fields = []
    for row in result:
        if 'email' in row[0].lower() or 'student' in row[0].lower():
            email_fields.append(row[0])
            print(f'  {row[0]} - {row[1]}')
    
    # Check sample data
    if email_fields:
        print("\n--- Sample FEEDBACK_REQUEST data ---")
        for field in email_fields:
            try:
                sample = db.execute(text(f'SELECT {field} FROM FEEDBACK_REQUEST WHERE {field} IS NOT NULL LIMIT 3')).fetchall()
                print(f'\n{field} samples:')
                for row in sample:
                    value = row[0]
                    is_encrypted = encryption.is_encrypted(value) if value else False
                    print(f'  {value[:30]}... (encrypted: {is_encrypted})')
            except Exception as e:
                print(f'  Error checking {field}: {e}')

if __name__ == "__main__":
    check_email_fields() 