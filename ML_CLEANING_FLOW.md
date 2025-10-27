# ML Data Cleaning Flow

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Raw Data (1,222 records)                    │
│  Issues: duplicates, typos, inconsistent formats, variations    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ML Data Cleaner                            │
│                   (ml_cleaner.py)                               │
└─────────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Step 1:    │    │   Step 2:    │    │   Step 3:    │
│   Format     │    │   Genre      │    │   Artist     │
│ Normalization│    │Normalization │    │  Clustering  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │   Step 4:    │
                    │    Title     │
                    │Normalization │
                    └──────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │   Step 5:    │
                    │  Duplicate   │
                    │   Removal    │
                    └──────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │   Step 6:    │
                    │     Data     │
                    │  Validation  │
                    └──────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Clean Data (~45 records)                      │
│        All duplicates removed, formats normalized               │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Step Breakdown

### Step 1: Format Normalization (Fuzzy Matching)

```
Input: "vynil", "casset", "recod", "8Trac"
                    ↓
┌─────────────────────────────────────────┐
│  Fuzzy String Matching Algorithm       │
│  - Remove special characters            │
│  - Calculate Levenshtein distance       │
│  - Match against known formats          │
│  - Threshold: 70% similarity            │
└─────────────────────────────────────────┘
                    ↓
Output: "Vinyl", "Cassette", "Vinyl", "8-Track"
```

**Algorithm:**
- Uses `fuzzywuzzy` library with Levenshtein distance
- Compares input against dictionary: `{cd, vinyl, cassette, digital, 8track, reel}`
- Handles common typos with pattern matching

### Step 2: Genre Normalization

```
Input: ["rok", "pop"], "Rock", ["Jazz"]
                    ↓
┌─────────────────────────────────────────┐
│  Genre Standardization                  │
│  - Handle array vs string               │
│  - Fix typos (rok → Rock)               │
│  - Apply title case                     │
│  - Take first genre if array            │
└─────────────────────────────────────────┘
                    ↓
Output: "Rok" → "Rock", "Rock", "Jazz"
```

### Step 3: Artist Clustering (ML Core)

```
Input: ["Green Day", "green-day", "GreenDay", "Greenday"]
                    ↓
┌─────────────────────────────────────────┐
│  Text Normalization                     │
│  Remove: spaces, hyphens, special chars │
│  Lowercase all                          │
└─────────────────────────────────────────┘
                    ↓
Normalized: ["greenday", "greenday", "greenday", "greenday"]
                    ↓
┌─────────────────────────────────────────┐
│  TF-IDF Vectorization                   │
│  - Character n-grams (2-3 chars)        │
│  - Creates feature vectors              │
└─────────────────────────────────────────┘
                    ↓
Feature Vectors: [[0.5, 0.3, ...], [0.5, 0.3, ...], ...]
                    ↓
┌─────────────────────────────────────────┐
│  DBSCAN Clustering                      │
│  - eps=0.3 (distance threshold)         │
│  - min_samples=1                        │
│  - metric='cosine'                      │
└─────────────────────────────────────────┘
                    ↓
Clusters: {0: ["Green Day", "green-day", "GreenDay", "Greenday"]}
                    ↓
┌─────────────────────────────────────────┐
│  Canonical Form Selection               │
│  Score based on:                        │
│  - Has spaces (+3)                      │
│  - Proper capitalization (+2)           │
│  - Length (+0.1 per char)               │
└─────────────────────────────────────────┘
                    ↓
Output: "Green Day" (selected as canonical)
```

**Why DBSCAN?**
- Density-based clustering works well for text similarity
- No need to specify number of clusters
- Handles noise (outliers) naturally
- Cosine distance ideal for TF-IDF vectors

### Step 4: Title Normalization

```
Input: "abbey road", "AbbeyRoad", "Abbey Road"
                    ↓
┌─────────────────────────────────────────┐
│  Title Case Conversion                  │
│  - Capitalize first letter of words     │
│  - Consistent formatting                │
└─────────────────────────────────────────┘
                    ↓
Output: "Abbey Road", "Abbeyroad", "Abbey Road"
```

### Step 5: Duplicate Removal (Composite Key)

```
Records:
1. Green Day - Dookie - 1994
2. green-day - Dookie - 1994
3. GreenDay - dookie - 1994
                    ↓
┌─────────────────────────────────────────┐
│  Create Composite Keys                  │
│  normalize(artist) + "|" +              │
│  normalize(title) + "|" + year          │
└─────────────────────────────────────────┘
                    ↓
Keys:
1. "greenday|dookie|1994"
2. "greenday|dookie|1994"  ← Same!
3. "greenday|dookie|1994"  ← Same!
                    ↓
┌─────────────────────────────────────────┐
│  Group by Composite Key                 │
│  Aggregate:                             │
│  - Most common format                   │
│  - Average price                        │
│  - Max sales                            │
└─────────────────────────────────────────┘
                    ↓
Output: 1 record (Green Day - Dookie - 1994)
```

### Step 6: Data Validation

```
Input: Mixed data types, possible NaN values
                    ↓
┌─────────────────────────────────────────┐
│  Type Validation & Coercion             │
│  - Ensure numeric fields are numeric    │
│  - Fill NaN with defaults               │
│  - Validate ranges                      │
└─────────────────────────────────────────┘
                    ↓
Output: Clean, validated data
```

## Performance Metrics

```
┌─────────────────────────────────────────────────────┐
│                  Cleaning Results                   │
├─────────────────────────────────────────────────────┤
│  Original Records:        1,222                     │
│  Cleaned Records:         ~45                       │
│  Duplicates Removed:      ~1,177 (96%)              │
│  Format Variations:       8+ → 5 standard           │
│  Artist Variations:       ~200 → ~40 unique         │
│  Processing Time:         ~2-5 seconds              │
└─────────────────────────────────────────────────────┘
```

## Example Transformation

### Before Cleaning:
```json
[
  {"artist": "Green Day", "format": "CD", "genre": "Punk Rock"},
  {"artist": "green-day", "format": "CD", "genre": "Punk Rock"},
  {"artist": "GreenDay", "format": "CD", "genre": ["Punk Rock"]},
  {"artist": "Greenday", "format": "Vinyl", "genre": "Punk Rock"},
  {"artist": "green day", "format": "CD", "genre": ["Punk", "Rock"]},
  {"artist": "some-band", "format": "vynil", "genre": ["rok", "pop"]},
  {"artist": "Classic Group", "format": "casset", "genre": ["Jazz"]}
]
```

### After Cleaning:
```json
[
  {"artist": "Green Day", "format": "CD", "genre": "Punk Rock", "price": 18.99},
  {"artist": "Some-Band", "format": "Vinyl", "genre": "Rok", "price": 19.99},
  {"artist": "Classic Group", "format": "Cassette", "genre": "Jazz", "price": 30.00}
]
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│         Machine Learning Stack          │
├─────────────────────────────────────────┤
│  scikit-learn    → Clustering, TF-IDF   │
│  pandas          → Data manipulation    │
│  numpy           → Numerical operations │
│  fuzzywuzzy      → Fuzzy matching       │
│  Levenshtein     → String distance      │
└─────────────────────────────────────────┘
```

## API Integration

```
Frontend (data.html)
        │
        │ HTTP GET
        ▼
┌──────────────────────┐
│  Flask Backend       │
│  /ml-clean-data      │
└──────────────────────┘
        │
        │ calls
        ▼
┌──────────────────────┐
│  MLDataCleaner       │
│  clean_data()        │
└──────────────────────┘
        │
        │ returns
        ▼
┌──────────────────────┐
│  Cleaned Data +      │
│  Report              │
└──────────────────────┘
        │
        │ JSON response
        ▼
Frontend displays results
```
