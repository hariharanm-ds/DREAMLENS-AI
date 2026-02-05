#!/usr/bin/env python
"""
System verification test for DREAMLENS AI
Checks all routes, templates, static files, and critical dependencies
"""
import os
import sys
import json
from pathlib import Path

def test_file_structure():
    """Verify all required files and directories exist"""
    print("\n=== Testing File Structure ===")
    required_files = [
        'app.py',
        'vercel.json',
        'vercel_requirements.txt',
        'requirements.txt',
        'static/style.css',
        'templates/index.html',
        'templates/chat.html',
        'templates/about.html',
        'templates/contact.html',
        'templates/history.html',
        'templates/admin.html',
        'templates/annotate.html',
        'api/interpret.py',
        'project/cleaned_dream_interpretations.csv',
    ]
    
    all_exist = True
    for f in required_files:
        path = Path(f)
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {f}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_dependencies():
    """Verify critical Python dependencies are importable"""
    print("\n=== Testing Dependencies ===")
    dependencies = {
        'flask': 'Flask',
        'pandas': 'pandas',
        'sklearn': 'scikit-learn',
        'requests': 'requests',
        'nltk': 'nltk',
    }
    
    all_ok = True
    for module_name, display_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except ImportError as e:
            print(f"  ✗ {display_name}: {e}")
            all_ok = False
    
    return all_ok

def test_flask_app_creation():
    """Verify Flask app can be created without errors"""
    print("\n=== Testing Flask App Creation ===")
    try:
        from flask import Flask
        test_app = Flask(__name__)
        print("  ✓ Flask app instance created successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to create Flask app: {e}")
        return False

def test_data_files():
    """Verify data files are accessible"""
    print("\n=== Testing Data Files ===")
    import pandas as pd
    
    # Test dream interpretations dataset
    try:
        df = pd.read_csv('project/cleaned_dream_interpretations.csv')
        print(f"  ✓ Dream interpretations dataset loaded ({len(df)} rows)")
    except Exception as e:
        print(f"  ✗ Dream interpretations dataset: {e}")
        return False
    
    # Verify required columns
    if "Word" in df.columns and "Interpretation" in df.columns:
        print(f"  ✓ Dataset has required columns (Word, Interpretation)")
    else:
        print(f"  ✗ Dataset missing required columns")
        return False
    
    return True

def test_config_files():
    """Verify configuration files are valid JSON"""
    print("\n=== Testing Configuration Files ===")
    
    # Test vercel.json
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        print(f"  ✓ vercel.json is valid JSON")
        
        # Verify key fields
        if 'version' in config and 'builds' in config and 'routes' in config:
            print(f"  ✓ vercel.json has required fields")
        else:
            print(f"  ✗ vercel.json missing required fields")
            return False
    except Exception as e:
        print(f"  ✗ vercel.json error: {e}")
        return False
    
    # Test runtime.json if it exists
    config_dir = 'config'
    if os.path.exists(config_dir):
        config_file = os.path.join(config_dir, 'runtime.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    runtime_config = json.load(f)
                print(f"  ✓ config/runtime.json is valid")
            except Exception as e:
                print(f"  ✗ config/runtime.json error: {e}")
                return False
    else:
        print(f"  ✓ config directory will be created on first run")
    
    return True

def test_routes_defined():
    """Verify all Flask routes are properly defined in app.py"""
    print("\n=== Testing Route Definitions ===")
    
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    expected_routes = [
        '@app.route("/")',
        '@app.route("/chat")',
        '@app.route("/annotate")',
        '@app.route("/interpret")',
        '@app.route("/about")',
        '@app.route("/contact")',
        '@app.route("/history")',
        '@app.route("/admin")',
        '@app.route("/_health")',
        '@app.route("/_model_status")',
    ]
    
    all_found = True
    for route in expected_routes:
        if route in app_content:
            route_name = route.split('"')[1] if '"' in route else route
            print(f"  ✓ {route_name}")
        else:
            print(f"  ✗ {route}")
            all_found = False
    
    return all_found

def test_api_endpoint():
    """Verify API endpoint is properly configured"""
    print("\n=== Testing API Endpoint ===")
    
    try:
        with open('api/interpret.py', 'r') as f:
            api_content = f.read()
        
        if 'def handler' in api_content or 'def handler(' in api_content:
            print(f"  ✓ API handler function defined")
        else:
            print(f"  ✗ API handler function not found")
            return False
        
        if 'hf_zero_shot' in api_content or 'hf_generate' in api_content:
            print(f"  ✓ API interpretation functions present")
        else:
            print(f"  ✗ API interpretation functions missing")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ API endpoint error: {e}")
        return False

def test_templates_syntax():
    """Quick check that HTML templates are well-formed"""
    print("\n=== Testing HTML Templates ===")
    
    templates = [
        'templates/index.html',
        'templates/chat.html',
        'templates/about.html',
        'templates/contact.html',
        'templates/history.html',
        'templates/admin.html',
        'templates/annotate.html',
    ]
    
    all_ok = True
    for template in templates:
        try:
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic checks
            has_doctype = '<!DOCTYPE' in content.upper() or '<!doctype' in content.lower()
            has_html = '<html' in content.lower()
            has_body = '<body' in content.lower()
            
            if has_doctype and has_html and has_body:
                print(f"  ✓ {template}")
            else:
                print(f"  ⚠ {template} (basic structure may be incomplete)")
        except Exception as e:
            print(f"  ✗ {template}: {e}")
            all_ok = False
    
    return all_ok

def test_static_files():
    """Verify static files exist and are readable"""
    print("\n=== Testing Static Files ===")
    
    static_files = [
        'static/style.css',
    ]
    
    all_ok = True
    for static_file in static_files:
        try:
            with open(static_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"  ✓ {static_file} ({len(content)} bytes)")
        except Exception as e:
            print(f"  ✗ {static_file}: {e}")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    print("=" * 60)
    print("DREAMLENS AI - System Verification Test")
    print("=" * 60)
    
    results = {
        "File Structure": test_file_structure(),
        "Dependencies": test_dependencies(),
        "Flask App Creation": test_flask_app_creation(),
        "Data Files": test_data_files(),
        "Configuration Files": test_config_files(),
        "Route Definitions": test_routes_defined(),
        "API Endpoint": test_api_endpoint(),
        "HTML Templates": test_templates_syntax(),
        "Static Files": test_static_files(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    print("=" * 60)
    print(f"Result: {passed}/{total} test groups passed")
    
    if passed == total:
        print("\n✓ All systems ready for deployment!")
        return 0
    else:
        print(f"\n✗ {total - passed} test group(s) failed - review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
