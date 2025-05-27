# User Data Encryption Implementation

This document describes the field-level encryption implementation for sensitive user data in the application.

## Overview

The encryption system protects sensitive user data using **Fernet symmetric encryption** from the `cryptography` library. It provides:

- **Transparent encryption/decryption** in the service layer
- **Key rotation support** for enhanced security
- **Backward compatibility** with existing unencrypted data
- **Secure key management** via environment variables

## Encrypted Fields

The following user fields are automatically encrypted:

- `email` - User email address (PII)
- `firstName` - User's first name (PII)
- `lastName` - User's last name (PII)
- `monashId` - Student/Staff ID number (sensitive identifier)
- `monashObjectId` - Unique system identifier

**Note:** `password` field remains hashed using bcrypt (not encrypted) as it doesn't need to be reversible.

## Setup Instructions

### 1. Generate Encryption Key

```bash
# Navigate to the user module directory
cd src/user

# Generate a new encryption key
python migration_script.py generate-key
```

This will output something like:

```
Generated new encryption key:
USER_ENCRYPTION_KEY=gAAAAABhZ1234567890abcdefghijklmnopqrstuvwxyz...

Add this to your .env file!
```

### 2. Add Key to Environment

Add the generated key to your `.env` file:

```env
# User Data Encryption
USER_ENCRYPTION_KEY=gAAAAABhZ1234567890abcdefghijklmnopqrstuvwxyz...

# Optional: For key rotation
# USER_ENCRYPTION_KEY_ROTATION=your_old_key_here
```

### 3. Verify Setup

```bash
python migration_script.py verify-setup
```

### 4. Migrate Existing Data (if applicable)

If you have existing unencrypted user data:

```bash
python migration_script.py migrate-data
```

## How It Works

### Encryption Flow

1. **Data Input** → User data comes in via API
2. **Service Layer** → `_prepare_user_data_for_storage()` encrypts sensitive fields
3. **Database** → Encrypted data is stored
4. **Retrieval** → `_prepare_user_data_for_response()` decrypts data for API response

### Key Features

#### Transparent Operation

```python
# Service functions automatically handle encryption/decryption
user = get_user_by_email(db, "john@example.com")  # Email is encrypted for lookup
# Returns decrypted user data for API response
```

#### Backward Compatibility

```python
# The system can handle both encrypted and unencrypted data
# Unencrypted legacy data is returned as-is with a warning
```

#### Key Rotation Support

```python
# Set both keys in environment:
# USER_ENCRYPTION_KEY=new_key
# USER_ENCRYPTION_KEY_ROTATION=old_key
# System will encrypt with new key, decrypt with either key
```

## Security Considerations

### Key Management

- **Environment Variables**: Keys are stored in environment variables, not in code
- **Key Rotation**: Supported for enhanced security
- **Key Generation**: Uses cryptographically secure random generation
- **Key Storage**: Store keys securely (e.g., AWS Secrets Manager, Azure Key Vault)

### Encryption Details

- **Algorithm**: Fernet (AES 128 in CBC mode with HMAC-SHA256)
- **Key Size**: 256-bit keys
- **Authentication**: Built-in message authentication prevents tampering
- **Timestamp**: Fernet includes timestamps for key rotation and expiration

### Best Practices

1. **Backup Keys Securely**: Store encryption keys in multiple secure locations
2. **Regular Key Rotation**: Rotate keys periodically (e.g., annually)
3. **Monitor Access**: Log and monitor access to encrypted data
4. **Secure Environment**: Ensure `.env` files are not committed to version control

## API Impact

### No Changes Required

The encryption is **completely transparent** to API consumers:

- **Request/Response Format**: Unchanged
- **Validation**: Works normally with Pydantic schemas
- **Error Handling**: Maintains existing error patterns

### Example API Usage

```python
# POST /api/user/signup
{
    "email": "john@example.com",      # Will be encrypted in database
    "firstName": "John",              # Will be encrypted in database
    "lastName": "Doe",                # Will be encrypted in database
    "monashId": "12345678",          # Will be encrypted in database
    "role": "Student",
    "faculty": "Engineering"
}

# Response (decrypted automatically)
{
    "email": "john@example.com",      # Decrypted for response
    "firstName": "John",              # Decrypted for response
    "lastName": "Doe",                # Decrypted for response
    "monashId": "12345678",          # Decrypted for response
    "role": "Student",
    "faculty": "Engineering"
}
```

## Database Queries

### Email Lookups

Email-based queries are automatically handled:

```python
# This works transparently
user = get_user_by_email(db, "john@example.com")

# Internally, the email is encrypted for database lookup:
# SELECT * FROM USER WHERE email = 'gAAAAABhZ...' (encrypted)
```

### Enrollment Queries

Student enrollment queries work with encrypted emails:

```python
# This works transparently
units = get_student_all_student_enrolled_units(db, "student@example.com")

# Internally uses encrypted email for JOIN operations
```

## Troubleshooting

### Common Issues

1. **Missing Encryption Key**

   ```
   Error: No USER_ENCRYPTION_KEY found in environment
   ```

   **Solution**: Add the encryption key to your `.env` file

2. **Decryption Failures**

   ```
   Warning: Returning original value - might be legacy unencrypted data
   ```

   **Solution**: Run the migration script to encrypt legacy data

3. **Key Rotation Issues**
   ```
   Error: Decryption failed for field
   ```
   **Solution**: Ensure both old and new keys are in environment during rotation

### Debugging

Enable detailed logging:

```python
import logging
logging.getLogger('src.user.encryption').setLevel(logging.DEBUG)
```

## Performance Considerations

### Encryption Overhead

- **Minimal Impact**: Fernet is highly optimized
- **Field-Level**: Only sensitive fields are encrypted
- **Caching**: Consider caching decrypted data for read-heavy operations

### Database Impact

- **Storage**: Encrypted fields are larger (base64 encoded)
- **Indexing**: Encrypted fields cannot be efficiently indexed
- **Queries**: Email lookups require exact encrypted value matching

## Migration Strategy

### For Existing Applications

1. **Deploy Encryption Code**: Deploy without migrating data
2. **Generate Keys**: Create and securely store encryption keys
3. **Test Setup**: Verify encryption works with test data
4. **Migrate Data**: Run migration script during maintenance window
5. **Monitor**: Watch for any decryption issues post-migration

### Rollback Plan

If issues arise:

1. **Keep Old Keys**: Don't delete old encryption keys
2. **Code Rollback**: Previous code version can read unencrypted data
3. **Data Recovery**: Encrypted data can be decrypted with proper keys

## Compliance

This encryption implementation helps with:

- **GDPR**: Protects personal data with strong encryption
- **FERPA**: Secures educational records
- **SOC 2**: Demonstrates data protection controls
- **ISO 27001**: Supports information security management

## Future Enhancements

Potential improvements:

1. **Hardware Security Modules (HSM)**: For enterprise key management
2. **Searchable Encryption**: For encrypted field queries
3. **Audit Logging**: Track all encryption/decryption operations
4. **Automatic Key Rotation**: Scheduled key rotation
5. **Field-Level Permissions**: Different encryption keys per field type
