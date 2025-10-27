#!/usr/bin/env python3
"""Test script for ML data cleaner"""
import sys
sys.path.insert(0, '/home/toby/cyber-mole-local/backend/app')

from ml_cleaner import MLDataCleaner
import json

# Load test data
with open('/home/toby/cyber-mole-local/training/data_set_1.json', 'r') as f:
    data = json.load(f)

print(f"Original data: {len(data)} records")
print("\nSample raw records (showing data quality issues):")
print("-" * 80)

# Show some problematic records
print("\n1. Format variations:")
for i, record in enumerate(data[:30]):
    if record.get('format') not in ['CD', 'Vinyl']:
        print(f"   {record.get('artist', 'N/A')}: format='{record.get('format', 'N/A')}'")

print("\n2. Artist name variations (Green Day):")
for record in data:
    if 'green' in record.get('artist', '').lower():
        print(f"   artist='{record.get('artist')}', title='{record.get('title')}'")

print("\n3. Genre inconsistencies:")
for i, record in enumerate(data[:10]):
    genre = record.get('genre')
    if isinstance(genre, list):
        print(f"   {record.get('artist')}: genre={genre} (array)")
    else:
        print(f"   {record.get('artist')}: genre='{genre}' (string)")

print("\n" + "=" * 80)
print("Running ML-based data cleaning...")
print("=" * 80)

# Clean the data
cleaner = MLDataCleaner()
cleaned_data = cleaner.clean_data(data)

print(f"\nCleaned data: {len(cleaned_data)} records")
print(f"Duplicates removed: {len(data) - len(cleaned_data)}")

# Generate report
report = cleaner.get_cleaning_report(data, cleaned_data)
print("\nCleaning Report:")
print(f"  - Original records: {report['original_count']}")
print(f"  - Cleaned records: {report['cleaned_count']}")
print(f"  - Duplicates removed: {report['duplicates_removed']}")
print(f"  - Formats normalized: {report['formats_normalized']}")

print("\nSample cleaned records:")
print("-" * 80)
for i, record in enumerate(cleaned_data[:5]):
    print(f"\n{i+1}. {record.get('artist')} - {record.get('title')}")
    print(f"   Format: {record.get('format')}")
    print(f"   Genre: {record.get('genre')}")
    print(f"   Price: ${record.get('price'):.2f}")
    print(f"   Sales: {record.get('sales'):,}")

print("\nChecking Green Day records after cleaning:")
green_day_records = [r for r in cleaned_data if 'green day' in r.get('artist', '').lower()]
print(f"Found {len(green_day_records)} Green Day record(s)")
for record in green_day_records:
    print(f"  - {record.get('artist')} - {record.get('title')} ({record.get('format')})")

print("\n" + "=" * 80)
print("ML Cleaning Test Complete!")
print("=" * 80)

# Save cleaned data
output_path = '/home/toby/cyber-mole-local/training/cleaned_data_test.json'
with open(output_path, 'w') as f:
    json.dump(cleaned_data, f, indent=2)
print(f"\nCleaned data saved to: {output_path}")
