#!/bin/bash

# Encryption Rollback Script
# This script helps you rollback from encryption backups

echo "🔄 Encryption Rollback Tool"
echo "============================"

# Activate virtual environment if it exists
if [ -d "learner_centered_feedback_env" ]; then
    echo "📦 Activating virtual environment..."
    source learner_centered_feedback_env/bin/activate
fi

# Check if backup file is provided as argument
if [ $# -eq 0 ]; then
    echo "📋 Listing available backups..."
    python migration/rollback_script.py
else
    echo "🔄 Rolling back from backup: $1"
    python migration/rollback_script.py "$1"
fi 