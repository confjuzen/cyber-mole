# ML Data Cleaning Troubleshooting Guide

## Error: "JSON.parse: unexpected character at line 1 column 1"

This error means the frontend couldn't parse the server response as JSON. Here's how to fix it:

### Solution 1: Check if Backend is Running

```bash
# Check if port 5004 is in use
lsof -i :5004

# If nothing shows up, the backend isn't running
```

**Fix:** Start the backend
```bash
cd /home/toby/cyber-mole-local
source venv/bin/activate
cd backend/app
python app.py
```

### Solution 2: Check Dependencies

```bash
# Run diagnostic script
cd /home/toby/cyber-mole-local
source venv/bin/activate
python diagnose_ml_issue.py
```

If dependencies are missing:
```bash
pip install -r backend/requirements.txt
```

### Solution 3: Check for Python Errors

The backend might be crashing before sending a response. Check the terminal where you started the backend for error messages.

Common issues:
- **ImportError**: Missing dependencies → Run `pip install -r backend/requirements.txt`
- **ModuleNotFoundError**: Wrong directory → Make sure you're in `backend/app`
- **SyntaxError**: Code issue → Check the error message

### Solution 4: Test the ML Cleaner Directly

```bash
cd /home/toby/cyber-mole-local
source venv/bin/activate
python test_cleaner_simple.py
```

If this works, the ML cleaner is fine. The issue is with the Flask app.

### Solution 5: Check CORS

If you see CORS errors in browser console:
- Make sure `flask-cors` is installed
- Check that `CORS(app)` is in `app.py`

### Solution 6: Check the Data File

```bash
# Verify the data file exists and is valid JSON
cat /home/toby/cyber-mole-local/training/data_set_1.json | python -m json.tool > /dev/null

# If it shows an error, the JSON is invalid
```

## Other Common Errors

### Error: "Module 'ml_cleaner' not found"

**Cause:** Python can't find the ml_cleaner module

**Fix:**
```bash
# Make sure you're in the right directory
cd /home/toby/cyber-mole-local/backend/app
python app.py

# Or set PYTHONPATH
export PYTHONPATH=/home/toby/cyber-mole-local/backend/app:$PYTHONPATH
```

### Error: "No module named 'sklearn'"

**Cause:** scikit-learn not installed

**Fix:**
```bash
source venv/bin/activate
pip install scikit-learn pandas numpy fuzzywuzzy python-Levenshtein
```

### Error: "externally-managed-environment"

**Cause:** Trying to install packages outside venv

**Fix:**
```bash
# Always activate venv first
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Error: "Address already in use"

**Cause:** Port 5004 is already in use

**Fix:**
```bash
# Find the process
lsof -i :5004

# Kill it
kill -9 <PID>

# Or use a different port in app.py
socketio.run(app, host='0.0.0.0', port=5005)
```

### Error: "Connection refused"

**Cause:** Backend not running or wrong URL

**Fix:**
1. Make sure backend is running on port 5004
2. Check frontend is using correct URL: `http://localhost:5004`
3. Try `http://127.0.0.1:5004` instead

### Error: Pandas groupby issues

**Cause:** Pandas version incompatibility

**Fix:** Already fixed in the code. If you still see issues:
```bash
pip install --upgrade pandas==2.1.4
```

## Step-by-Step Debugging

### 1. Test Python Environment
```bash
cd /home/toby/cyber-mole-local
source venv/bin/activate
python --version  # Should be 3.x
```

### 2. Test Dependencies
```bash
python -c "import sklearn, pandas, fuzzywuzzy; print('OK')"
```

### 3. Test ML Cleaner Module
```bash
python test_cleaner_simple.py
```

### 4. Test Flask App
```bash
cd backend/app
python -c "from app import app; print('OK')"
```

### 5. Start Backend with Verbose Output
```bash
cd backend/app
python app.py
# Watch for any error messages
```

### 6. Test API Endpoint
```bash
# In another terminal
curl http://localhost:5004/ml-clean-data
# Should return JSON
```

### 7. Check Browser Console
- Open browser DevTools (F12)
- Go to Console tab
- Look for error messages
- Check Network tab for failed requests

## Quick Fixes

### Reset Everything
```bash
cd /home/toby/cyber-mole-local

# Reinstall dependencies
source venv/bin/activate
pip install --force-reinstall -r backend/requirements.txt

# Restart backend
cd backend/app
python app.py
```

### Use the Startup Script
```bash
cd /home/toby/cyber-mole-local
chmod +x start_backend.sh
./start_backend.sh
```

### Run Diagnostics
```bash
cd /home/toby/cyber-mole-local
source venv/bin/activate
python diagnose_ml_issue.py
```

## Still Having Issues?

### Check These Files Exist:
- `/home/toby/cyber-mole-local/backend/app/ml_cleaner.py`
- `/home/toby/cyber-mole-local/backend/app/app.py`
- `/home/toby/cyber-mole-local/training/data_set_1.json`
- `/home/toby/cyber-mole-local/backend/requirements.txt`

### Verify File Contents:
```bash
# Check ml_cleaner.py has MLDataCleaner class
grep "class MLDataCleaner" backend/app/ml_cleaner.py

# Check app.py imports ml_cleaner
grep "from ml_cleaner import" backend/app/app.py

# Check requirements.txt has ML packages
grep "scikit-learn" backend/requirements.txt
```

### Get Detailed Error Info:

The frontend now shows detailed errors. Check:
1. Browser console (F12 → Console)
2. Network tab (F12 → Network)
3. Backend terminal output

### Manual Test:
```bash
cd /home/toby/cyber-mole-local
source venv/bin/activate

# Test in Python REPL
python
>>> import sys
>>> sys.path.insert(0, 'backend/app')
>>> from ml_cleaner import MLDataCleaner
>>> cleaner = MLDataCleaner()
>>> data = [{"artist": "Test", "title": "Song", "genre": "Rock", "price": 10, "release_year": 2000, "sales": 100, "historical_sales": 100, "format": "CD"}]
>>> result = cleaner.clean_data(data)
>>> print(result)
```

If this works, the ML cleaner is fine. The issue is with Flask/network.

## Contact Info

If you're still stuck, check:
- `ML_CLEANING_README.md` for usage
- `ML_CLEANING_FLOW.md` for architecture
- `IMPLEMENTATION_SUMMARY.md` for technical details
