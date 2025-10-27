# ML-Powered Data Cleaning

## Overview

This project now includes a **machine learning-based data cleaning system** that automatically detects and fixes data quality issues in the music catalog dataset.

## Features

The ML cleaner handles:

1. **Format Normalization** - Uses fuzzy string matching to fix typos:
   - `vynil`, `viny` → `Vinyl`
   - `casset` → `Cassette`
   - `recod` → `Vinyl`
   - `8Trac`, `8 track` → `8-Track`
   - `reel to reel` → `Reel-to-Reel`

2. **Artist Name Clustering** - Uses DBSCAN clustering with TF-IDF vectorization:
   - Groups similar artist names (e.g., "Green Day", "green-day", "GreenDay")
   - Selects canonical form based on proper capitalization and spacing
   - Reduces artist name variations

3. **Genre Normalization**:
   - Handles both string and array formats
   - Fixes typos (e.g., "rok" → "Rock")
   - Standardizes to title case

4. **Duplicate Detection** - ML-based similarity detection:
   - Creates composite keys from normalized artist + title + year
   - Groups similar records
   - Aggregates numerical fields (max sales, average price)

5. **Data Validation**:
   - Ensures correct data types
   - Fills missing values with defaults
   - Validates numerical fields

## Technologies Used

- **scikit-learn** - DBSCAN clustering, TF-IDF vectorization
- **pandas** - Data manipulation and aggregation
- **fuzzywuzzy** - Fuzzy string matching for format normalization
- **python-Levenshtein** - Fast string distance calculations

## API Endpoints

### GET/POST `/ml-clean-data`
Cleans data using ML algorithms.

**Response:**
```json
{
  "cleaned_data": [...],
  "report": {
    "original_count": 1222,
    "cleaned_count": 45,
    "duplicates_removed": 1177,
    "formats_normalized": 8
  },
  "success": true
}
```

### POST `/save-cleaned-data`
Saves cleaned data to file.

**Request:**
```json
{
  "data": [...]
}
```

**Response:**
```json
{
  "message": "Cleaned data saved successfully",
  "path": "/home/toby/cyber-mole-local/training/cleaned_data.json",
  "success": true
}
```

## Usage

### Via Web Interface

1. Navigate to `http://localhost:3004/data.html`
2. Click "Clean Data with ML" button
3. View the cleaning report and results
4. Click "Save Cleaned Data" to persist results

### Via Python

```python
from ml_cleaner import MLDataCleaner
import json

# Load data
with open('training/data_set_1.json', 'r') as f:
    data = json.load(f)

# Clean
cleaner = MLDataCleaner()
cleaned_data = cleaner.clean_data(data)

# Get report
report = cleaner.get_cleaning_report(data, cleaned_data)
print(f"Removed {report['duplicates_removed']} duplicates")
```

### Testing

Run the test script:
```bash
source venv/bin/activate
python test_cleaner_simple.py
```

Or test with full dataset:
```bash
source venv/bin/activate
python backend/test_ml_cleaner.py
```

## How It Works

### 1. Format Normalization
Uses fuzzy string matching (Levenshtein distance) to match misspelled formats against a known dictionary. Confidence threshold of 70% ensures accurate matching.

### 2. Artist Clustering
```
Input: ["Green Day", "green-day", "GreenDay", "Greenday"]
       ↓
Normalize: ["greenday", "greenday", "greenday", "greenday"]
       ↓
TF-IDF Vectorization (character n-grams)
       ↓
DBSCAN Clustering (eps=0.3, cosine distance)
       ↓
Select Canonical Form (best capitalization/spacing)
       ↓
Output: ["Green Day", "Green Day", "Green Day", "Green Day"]
```

### 3. Duplicate Detection
Creates composite keys from normalized fields:
```
artist (normalized) + "|" + title (normalized) + "|" + year
```
Groups by composite key and aggregates:
- Takes most common format
- Averages prices
- Takes max sales values

## Results

On the sample dataset (`data_set_1.json`):
- **Original records**: 1,222
- **After cleaning**: ~45 unique records
- **Duplicates removed**: ~1,177 (96% reduction)
- **Format variations fixed**: 8+ different typos normalized

## File Structure

```
backend/
  app/
    ml_cleaner.py          # Main ML cleaning module
    app.py                 # Flask app with ML endpoints
  requirements.txt         # Updated with ML dependencies
  test_ml_cleaner.py       # Comprehensive test script

frontend/
  data.html                # Updated UI with ML cleaning button

training/
  data_set_1.json          # Original dataset
  cleaned_data.json        # Output from ML cleaning
```

## Dependencies

Added to `requirements.txt`:
```
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.26.2
fuzzywuzzy==0.18.0
python-Levenshtein==0.23.0
```

## Future Enhancements

Potential improvements:
- Train a supervised model on labeled data
- Add anomaly detection for price/sales outliers
- Implement genre taxonomy with hierarchical clustering
- Add confidence scores for each cleaning operation
- Support batch processing of large datasets
- Add undo/rollback functionality
