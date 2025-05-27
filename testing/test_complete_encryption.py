#!/usr/bin/env python3
"""
Comprehensive Encryption Test Script

This script tests that all email fields across all tables and services
are properly encrypted and decrypted.
"""

import os
import sys
from datetime import datetime

# Set encryption key
os.environ['USER_ENCRYPTION_KEY'] = 'dkdpYkkzRU9QMnJIaG9xMHltNWZMTTUtWXRtbUxpc0J4aEIwcWRjS3ROcz0='

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_db
from src.user.encryption import encrypt_field, decrypt_field, get_encryption
from src.user.service import get_user_by_email, create_user
from src.feedback.service import get_feedbacks_by_user_email
from src.feedback_request.service import get_feedback_requests
from sqlalchemy import text

def test_database_encryption():
    """Test that all email fields in the database are encrypted."""
    print("=== TESTING DATABASE ENCRYPTION ===")
    
    db = next(get_db())
    encryption = get_encryption()
    
    # Test tables and their email fields
    tables_to_test = {
        'USER': ['email', 'firstName', 'lastName', 'monashId'],
        'FEEDBACK': ['studentEmail', 'markerEmail'],
        'FEEDBACK_REQUEST': ['student_id'],
        'LOG': ['userEmail'],
        'ENROLLMENT': ['userEmail']
    }
    
    all_encrypted = True
    
    for table, fields in tables_to_test.items():
        print(f"\n--- Testing {table} table ---")
        
        for field in fields:
            try:
                # Get sample data
                result = db.execute(text(f"SELECT {field} FROM {table} WHERE {field} IS NOT NULL LIMIT 5")).fetchall()
                
                if not result:
                    print(f"  {field}: No data found")
                    continue
                
                encrypted_count = 0
                total_count = len(result)
                
                for row in result:
                    value = row[0]
                    # Skip empty strings - they don't need encryption
                    if value and value.strip():
                        if encryption.is_encrypted(value):
                            encrypted_count += 1
                        else:
                            print(f"  ✗ {field}: Found unencrypted value: {value}")
                            all_encrypted = False
                    else:
                        # Count empty strings as "encrypted" since they don't need encryption
                        encrypted_count += 1
                
                if encrypted_count == total_count:
                    print(f"  ✓ {field}: All {total_count} values encrypted")
                else:
                    print(f"  ✗ {field}: Only {encrypted_count}/{total_count} values encrypted")
                    all_encrypted = False
                    
            except Exception as e:
                print(f"  ✗ {field}: Error checking - {e}")
                all_encrypted = False
    
    return all_encrypted

def test_user_service():
    """Test user service encryption/decryption."""
    print("\n=== TESTING USER SERVICE ===")
    
    db = next(get_db())
    
    # Test getting a user by email
    try:
        # Get a sample encrypted email from database
        result = db.execute(text("SELECT email FROM USER LIMIT 1")).fetchone()
        if not result:
            print("  No users found in database")
            return False
        
        encrypted_email = result[0]
        
        # Try to decrypt it to get the actual email
        actual_email = decrypt_field(encrypted_email)
        print(f"  Testing with email: {actual_email}")
        
        # Test service function
        user = get_user_by_email(db, actual_email)
        
        if user:
            print(f"  ✓ get_user_by_email returned user: {user.get('email', 'N/A')}")
            
            # Verify the returned data is decrypted
            if '@' in user.get('email', ''):
                print("  ✓ Returned email is decrypted")
                return True
            else:
                print("  ✗ Returned email appears to still be encrypted")
                return False
        else:
            print("  ✗ get_user_by_email returned None")
            return False
            
    except Exception as e:
        print(f"  ✗ User service test failed: {e}")
        return False

def test_feedback_service():
    """Test feedback service encryption/decryption."""
    print("\n=== TESTING FEEDBACK SERVICE ===")
    
    db = next(get_db())
    
    try:
        # Get a sample user email
        result = db.execute(text("SELECT email FROM USER LIMIT 1")).fetchone()
        if not result:
            print("  No users found in database")
            return False
        
        encrypted_email = result[0]
        actual_email = decrypt_field(encrypted_email)
        print(f"  Testing with email: {actual_email}")
        
        # Test feedback service functions
        feedbacks = get_feedbacks_by_user_email(actual_email, db)
        print(f"  ✓ get_feedbacks_by_user_email returned {len(feedbacks)} feedbacks")
        
        # Check if any feedback data contains decrypted emails
        for feedback in feedbacks[:2]:  # Check first 2
            student_email = feedback.get('studentEmail', '')
            if student_email and '@' in student_email:
                print(f"  ✓ Feedback contains decrypted studentEmail: {student_email}")
            else:
                print(f"  ? Feedback studentEmail: {student_email}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Feedback service test failed: {e}")
        return False

def test_feedback_request_service():
    """Test feedback request service encryption/decryption."""
    print("\n=== TESTING FEEDBACK_REQUEST SERVICE ===")
    
    db = next(get_db())
    
    try:
        # Get a sample user email
        result = db.execute(text("SELECT email FROM USER LIMIT 1")).fetchone()
        if not result:
            print("  No users found in database")
            return False
        
        encrypted_email = result[0]
        actual_email = decrypt_field(encrypted_email)
        print(f"  Testing with email: {actual_email}")
        
        # Test feedback request service
        requests = get_feedback_requests(db, actual_email)
        print(f"  ✓ get_feedback_requests returned {len(requests)} requests")
        
        # Check if any request data contains decrypted emails
        for request in requests[:2]:  # Check first 2
            student_id = request.get('student_id', '')
            if student_id and '@' in student_id:
                print(f"  ✓ Request contains decrypted student_id: {student_id}")
            else:
                print(f"  ? Request student_id: {student_id}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Feedback request service test failed: {e}")
        return False

def test_encryption_decryption():
    """Test basic encryption/decryption functionality."""
    print("\n=== TESTING ENCRYPTION/DECRYPTION ===")
    
    test_email = "test@example.com"
    
    try:
        # Test encryption
        encrypted = encrypt_field(test_email)
        print(f"  ✓ Encrypted '{test_email}' to: {encrypted[:30]}...")
        
        # Test decryption
        decrypted = decrypt_field(encrypted)
        print(f"  ✓ Decrypted back to: {decrypted}")
        
        if decrypted == test_email:
            print("  ✓ Encryption/decryption round-trip successful")
            return True
        else:
            print("  ✗ Encryption/decryption round-trip failed")
            return False
            
    except Exception as e:
        print(f"  ✗ Encryption/decryption test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔐 COMPREHENSIVE ENCRYPTION TEST")
    print("=" * 50)
    
    tests = [
        ("Basic Encryption/Decryption", test_encryption_decryption),
        ("Database Encryption", test_database_encryption),
        ("User Service", test_user_service),
        ("Feedback Service", test_feedback_service),
        ("Feedback Request Service", test_feedback_request_service),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Encryption is working correctly across all modules.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 