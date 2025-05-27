# User Data Encryption Guide

Simple guide for encrypting user data and managing backups.

## 🚀 Production Migration

### 1. Set Encryption Key

```bash
# Generate encryption key (run once)
python -c "from cryptography.fernet import Fernet; import base64; key = Fernet.generate_key(); print('USER_ENCRYPTION_KEY=' + base64.urlsafe_b64encode(key).decode())"

# Add the output to your .env file
echo "USER_ENCRYPTION_KEY=your_generated_key_here" >> .env
```

### 2. Run Migration

```bash
# Migrate to encrypted format (creates automatic backup)
./migrate.sh
```

### 3. Rollback (if needed)

```bash
# List available backups
./rollback.sh

# Restore from specific backup
./rollback.sh migration_backups/user_data_backup_YYYYMMDD_HHMMSS.json
```

## 🧪 Testing

```bash
# Decrypt data for testing (testing only!)
./testing/decrypt-rollback.sh

# Test migration
./migrate.sh

# Test rollback
./rollback.sh migration_backups/user_data_backup_YYYYMMDD_HHMMSS.json
```

## 📝 What Gets Encrypted

- **USER table**: email, firstName, lastName, monashId, monashObjectId
- **FEEDBACK table**: studentEmail, markerEmail
- **LOG table**: userEmail
- **FEEDBACK_REQUEST table**: student_id

## ⚠️ Important Notes

- **Backup files** are created automatically in `migration_backups/`
- **Keep backups safe** - they contain unencrypted data
- **Store encryption key securely** - data cannot be recovered without it
- **Migration is idempotent** - safe to run multiple times
