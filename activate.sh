#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define virtual environment name
VENV_NAME="learner_centered_feedback_env"

# Check if virtual environment exists
if [ ! -d "$VENV_NAME" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating a new one...${NC}"
    python3 -m venv $VENV_NAME
    
    # Check if venv creation was successful
    if [ ! -d "$VENV_NAME" ]; then
        echo -e "\033[0;31mFailed to create virtual environment. Check if python3-venv is installed.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Virtual environment created successfully!${NC}"
    
    # Activate the virtual environment
    source $VENV_NAME/bin/activate
    
    echo -e "${BLUE}Installing required packages...${NC}"
    pip install playwright
    python -m playwright install
    
    echo -e "${GREEN}All dependencies installed successfully!${NC}"
else
    echo -e "${BLUE}Virtual environment found. Activating...${NC}"
    source $VENV_NAME/bin/activate
fi

echo -e "${GREEN}Virtual environment is now active.${NC}"
echo -e "${YELLOW}You can now run your script with:${NC} python cityline_bypass.py"
echo -e "${YELLOW}When done, run:${NC} ./deactivate.sh"
echo ""
echo -e "${GREEN}Your prompt should now show ($VENV_NAME) at the beginning.${NC}"

# Change PS1 to make it more obvious that we're in a virtual environment
PS1="($VENV_NAME) $PS1"

# Note: This line ensures that bash will use this shell
exec "$BASH" 