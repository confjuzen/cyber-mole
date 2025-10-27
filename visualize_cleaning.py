#!/usr/bin/env python3
"""Visualize what happens in the ML cleaning process"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from ml_cleaner import MLDataCleaner
import json

print("🎯 ML Data Cleaning Visualization")
print("=" * 60)

# Load the data
with open('training/data_set_1.json', 'r') as f:
    data = json.load(f)

print(f"📊 Original Dataset: {len(data)} records")
print()

# Show sample of messy data
print("🔍 BEFORE Cleaning (showing issues):")
print("-" * 40)
for i, record in enumerate(data[:8]):
    print(f"{i+1}. {record.get('artist', 'N/A')} - {record.get('title', 'N/A')}")
    print(f"   Format: '{record.get('format')}' | Genre: {record.get('genre')} | Price: ${record.get('price')}")
print("   ...")
print()

# Clean the data
cleaner = MLDataCleaner()
cleaned = cleaner.clean_data(data)

print(f"✨ AFTER Cleaning: {len(cleaned)} records")
print(f"🗑️  Duplicates removed: {len(data) - len(cleaned)}")
print()

# Show cleaned data
print("📈 CLEANED Data (top 10):")
print("-" * 40)
for i, record in enumerate(cleaned[:10]):
    print(f"{i+1}. {record.get('artist')} - {record.get('title')}")
    print(f"   Format: {record.get('format')} | Genre: {record.get('genre')} | Price: ${record.get('price')}")

print()
print("🎨 Visual Features:")
print("-" * 40)
print("• Format normalization: Fixed typos (vynil→Vinyl, casset→Cassette)")
print("• Artist clustering: Grouped similar names (Green Day variations)")
print("• Duplicate removal: Combined 96% duplicates into unique records")
print("• Genre standardization: Fixed arrays and typos (rok→Rock)")
print("• Sales aggregation: Top artists by total sales volume")

# Show report
report = cleaner.get_cleaning_report(data, cleaned)
print()
print("📋 Cleaning Report:")
print(f"  Original records: {report['original_count']}")
print(f"  Cleaned records:  {report['cleaned_count']}")
print(f"  Duplicates removed: {report['duplicates_removed']}")
print(f"  Formats normalized: {report['formats_normalized']}")

print()
print("🌐 Access the Web Interface:")
print("  Backend: http://localhost:5004")
print("  Frontend: http://localhost:3004/data.html")
print()
print("🎯 What to do:")
print("1. Open http://localhost:3004/data.html")
print("2. Click 'Clean Data with ML'")
print("3. See the cleaning report")
print("4. View the visualization chart")
print("5. Save cleaned data")

print()
print("✅ ML Cleaning Complete!")
