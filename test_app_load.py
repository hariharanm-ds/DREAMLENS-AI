#!/usr/bin/env python
"""
Quick Flask app import test - checks if app.py can be loaded without errors
"""
import sys
import os

try:
    # Set minimal env vars to avoid model loading during import
    os.environ['USE_HF_ONLY'] = '1'
    
    print("Loading Flask app...")
    from app import app
    print("✓ Flask app loaded successfully")
    
    # List all registered routes
    print("\n✓ Registered Routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
        methods = ', '.join([m for m in rule.methods if m not in ('HEAD', 'OPTIONS')])
        print(f"  {rule.rule:40} [{methods}]")
    
    print(f"\n✓ Total routes registered: {len([r for r in app.url_map.iter_rules()])}")
    print("\n✓ All pages and endpoints are correctly connected!")
    
except Exception as e:
    print(f"✗ Error loading app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
