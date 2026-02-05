#!/usr/bin/env python
"""
Integration test - Verify all endpoints return proper responses
"""
import os
import sys
import json

# Minimize imports to test core functionality
os.environ['USE_HF_ONLY'] = '1'

from flask import Flask
from app import app

def test_endpoints():
    """Test all key endpoints"""
    print("\n=== Integration Tests - Endpoint Responses ===\n")
    
    with app.test_client() as client:
        tests_passed = 0
        tests_failed = 0
        
        # Test 1: Home page (/)
        print("Test 1: GET /")
        try:
            resp = client.get('/')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            assert b'DREAMLENS' in resp.data or b'dreamlens' in resp.data.lower(), "Home page content missing"
            print("  ✓ PASS - Home page loads\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 2: Chat page (/chat)
        print("Test 2: GET /chat")
        try:
            resp = client.get('/chat')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            assert b'dream' in resp.data.lower(), "Chat page content missing"
            print("  ✓ PASS - Chat page loads\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 3: About page (/about)
        print("Test 3: GET /about")
        try:
            resp = client.get('/about')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            assert b'about' in resp.data.lower(), "About page content missing"
            print("  ✓ PASS - About page loads\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 4: Contact page (/contact)
        print("Test 4: GET /contact")
        try:
            resp = client.get('/contact')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            assert b'contact' in resp.data.lower(), "Contact page content missing"
            print("  ✓ PASS - Contact page loads\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 5: History page (/history)
        print("Test 5: GET /history")
        try:
            resp = client.get('/history')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            assert b'history' in resp.data.lower(), "History page content missing"
            print("  ✓ PASS - History page loads\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 6: Admin page (/admin)
        print("Test 6: GET /admin")
        try:
            resp = client.get('/admin')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            assert b'admin' in resp.data.lower(), "Admin page content missing"
            print("  ✓ PASS - Admin page loads\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 7: Annotate page (/annotate)
        print("Test 7: GET /annotate")
        try:
            resp = client.get('/annotate')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            assert b'annotate' in resp.data.lower() or b'dream' in resp.data.lower(), "Annotate page content missing"
            print("  ✓ PASS - Annotate page loads\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 8: Health check (/_health)
        print("Test 8: GET /_health")
        try:
            resp = client.get('/_health')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            data = json.loads(resp.data)
            assert data.get('status') == 'ok', "Health status not OK"
            print("  ✓ PASS - Health check OK\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 9: Model status (/_model_status)
        print("Test 9: GET /_model_status")
        try:
            resp = client.get('/_model_status')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            data = json.loads(resp.data)
            assert 'zero_shot_loaded' in data, "Model status response incomplete"
            print("  ✓ PASS - Model status endpoint OK\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 10: Environment check (/_env_check)
        print("Test 10: GET /_env_check")
        try:
            resp = client.get('/_env_check')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            data = json.loads(resp.data)
            assert 'python_version' in data, "Env check response incomplete"
            print("  ✓ PASS - Environment check OK\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 11: History API (/history/recent)
        print("Test 11: GET /history/recent")
        try:
            resp = client.get('/history/recent')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            data = json.loads(resp.data)
            assert 'items' in data, "History response missing items"
            print("  ✓ PASS - History API OK\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 12: Annotations API (/annotations/recent)
        print("Test 12: GET /annotations/recent")
        try:
            resp = client.get('/annotations/recent')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            data = json.loads(resp.data)
            assert 'recent' in data, "Annotations response missing recent"
            print("  ✓ PASS - Annotations API OK\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 13: Interpret API - valid dream
        print("Test 13: POST /interpret (valid dream)")
        try:
            payload = {'dream': 'I was flying through clouds'}
            resp = client.post('/interpret', 
                             json=payload,
                             content_type='application/json')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            data = json.loads(resp.data)
            assert data.get('success') == True, "Interpret failed"
            assert 'dream' in data, "Response missing dream"
            assert 'interpretation' in data, "Response missing interpretation"
            print("  ✓ PASS - Interpret API works\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 14: Interpret API - empty dream
        print("Test 14: POST /interpret (no dream - should fail)")
        try:
            payload = {'dream': ''}
            resp = client.post('/interpret', 
                             json=payload,
                             content_type='application/json')
            assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
            data = json.loads(resp.data)
            assert data.get('success') == False, "Should have failed"
            print("  ✓ PASS - Error handling works\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Test 15: Static files
        print("Test 15: GET /static/style.css")
        try:
            resp = client.get('/static/style.css')
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            assert len(resp.data) > 100, "CSS file too small"
            print("  ✓ PASS - Static files served\n")
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL - {e}\n")
            tests_failed += 1
        
        # Summary
        print("=" * 60)
        print(f"Results: {tests_passed} passed, {tests_failed} failed")
        print("=" * 60)
        
        return tests_failed == 0

if __name__ == "__main__":
    try:
        success = test_endpoints()
        if success:
            print("\n✓ All integration tests passed!")
            print("✓ System is ready for deployment")
            sys.exit(0)
        else:
            print("\n✗ Some integration tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
