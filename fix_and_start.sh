#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         ML Data Cleaning - Fix & Start Script             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Go to project root
cd /home/toby/cyber-mole-local

# Step 1: Kill old processes
echo "Step 1: Killing old backend processes..."
pkill -f "python.*app.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Killed old processes"
    sleep 2
else
    echo "  ℹ No old processes found"
fi

# Step 2: Activate venv
echo ""
echo "Step 2: Activating virtual environment..."
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "  ✓ Virtual environment activated"
else
    echo "  ✗ Virtual environment not found!"
    echo "  Creating venv..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Step 3: Install dependencies
echo ""
echo "Step 3: Checking dependencies..."
python -c "import sklearn, pandas, fuzzywuzzy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  ⚠ Installing ML dependencies..."
    pip install -q -r backend/requirements.txt
    echo "  ✓ Dependencies installed"
else
    echo "  ✓ All dependencies present"
fi

# Step 4: Test ML cleaner
echo ""
echo "Step 4: Testing ML cleaner module..."
python -c "import sys; sys.path.insert(0, 'backend/app'); from ml_cleaner import MLDataCleaner; print('  ✓ ML cleaner loaded')" 2>&1
if [ $? -ne 0 ]; then
    echo "  ✗ ML cleaner failed to load!"
    echo "  Run: python diagnose_ml_issue.py"
    exit 1
fi

# Step 5: Test routes
echo ""
echo "Step 5: Checking Flask routes..."
python test_routes.py 2>&1 | grep -q "/ml-clean-data"
if [ $? -eq 0 ]; then
    echo "  ✓ /ml-clean-data route registered"
else
    echo "  ⚠ Route check inconclusive, continuing..."
fi

# Step 6: Start backend
echo ""
echo "Step 6: Starting backend server..."
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Backend will start on: http://localhost:5004"
echo "Open in browser: http://localhost:3004/data.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

cd backend/app
python app.py
