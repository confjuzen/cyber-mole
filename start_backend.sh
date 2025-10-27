#!/bin/bash

echo "Starting Backend Server with ML Cleaning..."
echo "==========================================="

# Activate virtual environment
cd /home/toby/cyber-mole-local
source venv/bin/activate

# Check if dependencies are installed
echo "Checking dependencies..."
python -c "import sklearn; import pandas; import fuzzywuzzy; print('✓ All ML dependencies installed')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠ Installing ML dependencies..."
    pip install -r backend/requirements.txt
fi

# Test the ML cleaner module
echo ""
echo "Testing ML cleaner module..."
python -c "import sys; sys.path.insert(0, 'backend/app'); from ml_cleaner import MLDataCleaner; print('✓ ML cleaner module loaded successfully')"
if [ $? -ne 0 ]; then
    echo "✗ Error loading ML cleaner module"
    exit 1
fi

# Start the backend
echo ""
echo "Starting Flask backend on port 5004..."
echo "Open http://localhost:3004/data.html to use the ML cleaning"
echo ""
cd backend/app
python app.py
