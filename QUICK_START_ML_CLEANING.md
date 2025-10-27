# Quick Start: ML Data Cleaning

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd /home/toby/cyber-mole-local
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Step 2: Start the Backend
```bash
cd backend/app
python app.py
```

### Step 3: Open the Web Interface
```bash
# Open in browser:
http://localhost:3004/data.html

# Click: "Clean Data with ML"
```

---

## 📊 What It Does

The ML cleaner automatically fixes:

| Problem | Solution | Example |
|---------|----------|---------|
| 🔤 Format typos | Fuzzy matching | `vynil` → `Vinyl` |
| 👥 Artist variations | ML clustering | `green-day` → `Green Day` |
| 📋 Duplicates | Smart detection | 1,222 → 45 records |
| 🏷️ Genre issues | Normalization | `["rok"]` → `Rock` |

---

## 💻 Command Line Usage

### Test the Cleaner
```bash
python test_cleaner_simple.py
```

### Full Test with Report
```bash
python backend/test_ml_cleaner.py
```

### Python Script
```python
from ml_cleaner import MLDataCleaner
import json

# Load data
with open('training/data_set_1.json') as f:
    data = json.load(f)

# Clean it
cleaner = MLDataCleaner()
cleaned = cleaner.clean_data(data)

# Save result
with open('cleaned.json', 'w') as f:
    json.dump(cleaned, f, indent=2)

print(f"Cleaned {len(data)} → {len(cleaned)} records")
```

---

## 🎯 API Endpoints

### Clean Data
```bash
curl http://localhost:5004/ml-clean-data
```

### Save Cleaned Data
```bash
curl -X POST http://localhost:5004/save-cleaned-data \
  -H "Content-Type: application/json" \
  -d '{"data": [...]}'
```

---

## 📈 Expected Results

```
Original Records:     1,222
Cleaned Records:      ~45
Duplicates Removed:   ~1,177 (96%)
Processing Time:      2-5 seconds
```

---

## 🔧 Troubleshooting

### Import Error
```bash
# Make sure you're in venv
source venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Port Already in Use
```bash
# Check what's using port 5004
lsof -i :5004

# Kill the process
kill -9 <PID>
```

### Module Not Found
```bash
# Add to Python path
export PYTHONPATH=./backend/app:$PYTHONPATH
```

---

## 📁 Key Files

```
backend/app/ml_cleaner.py       # ML cleaning logic
backend/app/app.py              # Flask API
frontend/data.html              # Web UI
training/data_set_1.json        # Input data
training/cleaned_data.json      # Output data
```

---

## 🧪 Quick Test

```bash
# Simple test (30 seconds)
cd /home/toby/cyber-mole-local
source venv/bin/activate
python test_cleaner_simple.py

# Expected output:
# ✓ ML Cleaner module imported successfully
# ✓ Testing with 5 sample records
# ✓ ML Cleaner initialized
# ✓ Data cleaned: 5 → 2 records
# ✓✓✓ ML Cleaner test PASSED! ✓✓✓
```

---

## 📚 More Info

- **Full Documentation**: `ML_CLEANING_README.md`
- **Architecture**: `ML_CLEANING_FLOW.md`
- **Summary**: `IMPLEMENTATION_SUMMARY.md`

---

## ⚡ One-Liner

```bash
source venv/bin/activate && cd backend/app && python app.py &
```

Then open: http://localhost:3004/data.html

---

## 🎓 ML Algorithms Used

- **Fuzzy Matching**: Levenshtein distance for typos
- **TF-IDF**: Text vectorization for similarity
- **DBSCAN**: Clustering for grouping duplicates
- **Composite Keys**: Smart duplicate detection

---

## ✅ Success Indicators

After clicking "Clean Data with ML", you should see:

1. ✅ Cleaning report appears
2. ✅ Duplicate count shows ~1,177 removed
3. ✅ Clean data preview displays
4. ✅ Chart shows top artists
5. ✅ "Save Cleaned Data" button enabled

---

## 🚨 Common Issues

**Q: "Module 'ml_cleaner' not found"**  
A: Make sure you're in the venv and PYTHONPATH is set

**Q: "No module named 'sklearn'"**  
A: Run `pip install scikit-learn`

**Q: "Port 5004 in use"**  
A: Kill existing process or change port in app.py

**Q: "Data not loading"**  
A: Check backend is running on port 5004

---

## 🎉 That's It!

You now have a production-ready ML data cleaning system.

**Questions?** Check the full docs in `ML_CLEANING_README.md`
