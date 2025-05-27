#!/bin/bash

# Encryption Migration Script
# This script runs the automatic encryption migration with backup

echo "🚀 Starting Encryption Migration..."
echo "=================================="

# Activate virtual environment if it exists
if [ -d "learner_centered_feedback_env" ]; then
    echo "📦 Activating virtual environment..."
    source learner_centered_feedback_env/bin/activate
fi

# Run the migration script
echo "🔄 Running migration script..."
python migration/migration_script.py

echo "✅ Migration script completed!"
echo "📦 Check migration_backups/ directory for backup files" 