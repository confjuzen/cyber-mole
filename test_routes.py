#!/usr/bin/env python3
"""Test Flask routes are registered"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))

print("Testing Flask app routes...")
print("=" * 60)

try:
    from app import app
    print("✓ Flask app imported successfully")
    
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"  {rule.rule:30s} [{methods}]")
    
    # Check if our ML route exists
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    
    if '/ml-clean-data' in routes:
        print("\n✓ /ml-clean-data route is registered!")
    else:
        print("\n✗ /ml-clean-data route NOT found!")
        print("   This means there was an error loading the route.")
        
    if '/raw-data' in routes:
        print("✓ /raw-data route is registered!")
    else:
        print("✗ /raw-data route NOT found!")
        
except Exception as e:
    print(f"✗ Error loading Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("If /ml-clean-data is registered, the issue is:")
print("  1. Backend running from wrong directory")
print("  2. Port mismatch (check if using 5004)")
print("  3. Old backend process still running")
print("\nTo fix:")
print("  1. Kill any old backend: pkill -f 'python.*app.py'")
print("  2. Start fresh: cd backend/app && python app.py")
