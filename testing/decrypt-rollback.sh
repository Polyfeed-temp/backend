#!/bin/bash

# Decrypt Rollback Script (For Testing Only)
# This script reverts encrypted data back to unencrypted format for testing

echo "🔓 Decrypt Rollback Tool (Testing Only)"
echo "========================================"
echo "⚠️  WARNING: This will decrypt all encrypted data back to plaintext!"
echo "This is intended for testing the migration script with backup functionality."
echo ""

# Activate virtual environment if it exists
if [ -d "learner_centered_feedback_env" ]; then
    echo "📦 Activating virtual environment..."
    source learner_centered_feedback_env/bin/activate
fi

# Run the decrypt rollback script
echo "🔄 Running decrypt rollback script..."
python migration/decrypt_rollback_script.py 