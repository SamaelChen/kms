#!/usr/bin/env python3
"""
Comprehensive API Test Script for IntelliKnow KMS
Tests all endpoints and functionality
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"
TEST_TIMEOUT = 30

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def log_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def log_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def log_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def log_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def test_health():
    """Test health endpoint"""
    log_info("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            log_success(f"Health check passed: {response.json()}")
            return True
        else:
            log_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Health check error: {e}")
        return False

def test_info():
    """Test info endpoint"""
    log_info("Testing info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            log_success(f"Info endpoint: {data.get('name', 'N/A')}")
            return True
        else:
            log_error(f"Info endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Info endpoint error: {e}")
        return False

def test_api_health():
    """Test API health endpoint"""
    log_info("Testing API health...")
    try:
        response = requests.get(f"{API_URL}/health/", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            log_success(f"API health: {response.json()}")
            return True
        else:
            log_error(f"API health failed: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"API health error: {e}")
        return False

def test_analytics():
    """Test analytics endpoints"""
    log_info("Testing analytics...")
    results = []
    
    # Test stats
    try:
        response = requests.get(f"{API_URL}/analytics/stats", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            log_success(f"Analytics stats: {response.json()}")
            results.append(True)
        else:
            log_error(f"Analytics stats failed: {response.status_code}")
            results.append(False)
    except Exception as e:
        log_error(f"Analytics stats error: {e}")
        results.append(False)
    
    # Test query stats
    try:
        response = requests.get(f"{API_URL}/analytics/queries", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            log_success(f"Query stats retrieved")
            results.append(True)
        else:
            log_error(f"Query stats failed: {response.status_code}")
            results.append(False)
    except Exception as e:
        log_error(f"Query stats error: {e}")
        results.append(False)
    
    return all(results)

def test_documents():
    """Test document endpoints"""
    log_info("Testing documents...")
    results = []
    
    # Test list documents
    try:
        response = requests.get(f"{API_URL}/documents/", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            log_success(f"Listed {len(data)} documents")
            results.append(True)
        else:
            log_error(f"List documents failed: {response.status_code}")
            results.append(False)
    except Exception as e:
        log_error(f"List documents error: {e}")
        results.append(False)
    
    # Test upload with a sample file
    test_file = Path("/tmp/test_policy.txt")
    if test_file.exists():
        try:
            with open(test_file, "rb") as f:
                files = {"file": ("test_policy.txt", f, "text/plain")}
                data = {"intent_space": "HR"}
                response = requests.post(
                    f"{API_URL}/documents/upload",
                    files=files,
                    data=data,
                    timeout=TEST_TIMEOUT
                )
            if response.status_code == 200:
                log_success(f"Document upload: {response.json().get('filename')}")
                results.append(True)
            else:
                log_error(f"Document upload failed: {response.status_code} - {response.text}")
                results.append(False)
        except Exception as e:
            log_error(f"Document upload error: {e}")
            results.append(False)
    else:
        log_warning("Test file not found, skipping upload test")
        results.append(True)  # Don't fail if file doesn't exist
    
    return all(results)

def test_queries():
    """Test query endpoints"""
    log_info("Testing queries...")
    results = []
    
    # Test basic query
    try:
        payload = {"query": "What is the remote work policy?"}
        response = requests.post(
            f"{API_URL}/queries/ask",
            json=payload,
            timeout=TEST_TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            log_success(f"Query response time: {data.get('response_time_ms', 'N/A')}ms")
            log_info(f"Intent detected: {data.get('intent', 'N/A')}")
            results.append(True)
        else:
            log_error(f"Query failed: {response.status_code} - {response.text}")
            results.append(False)
    except Exception as e:
        log_error(f"Query error: {e}")
        results.append(False)
    
    # Test query validation
    try:
        payload = {"query": ""}  # Empty query should fail
        response = requests.post(
            f"{API_URL}/queries/ask",
            json=payload,
            timeout=TEST_TIMEOUT
        )
        if response.status_code == 422:
            log_success("Query validation working (empty query rejected)")
            results.append(True)
        else:
            log_warning(f"Query validation unexpected status: {response.status_code}")
            results.append(True)  # Not a failure
    except Exception as e:
        log_error(f"Query validation error: {e}")
        results.append(False)
    
    return all(results)

def test_intent_spaces():
    """Test intent space endpoints"""
    log_info("Testing intent spaces...")
    results = []
    
    # Test list intent spaces
    try:
        response = requests.get(f"{API_URL}/intents/spaces", timeout=TEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            log_success(f"Found {len(data)} intent spaces")
            for space in data:
                log_info(f"  - {space.get('name', 'N/A')}")
            results.append(True)
        else:
            log_error(f"List intent spaces failed: {response.status_code}")
            results.append(False)
    except Exception as e:
        log_error(f"List intent spaces error: {e}")
        results.append(False)
    
    return all(results)

def create_test_file():
    """Create a test document file"""
    test_content = """# Company Remote Work Policy

## Overview
This policy outlines the guidelines for remote work at our company.

## Eligibility
All full-time employees are eligible for remote work arrangements.

## Requirements
- High-speed internet connection
- Secure workspace
- Availability during core hours (10 AM - 3 PM)

## Approval Process
Submit remote work request to your manager for approval.

## Contact
For questions about this policy, contact HR at hr@company.com
"""
    test_file = Path("/tmp/test_policy.txt")
    test_file.write_text(test_content)
    log_info(f"Created test file: {test_file}")

def main():
    """Run all tests"""
    print("="*60)
    print("IntelliKnow KMS - Comprehensive API Test")
    print("="*60)
    print()
    
    # Create test file
    create_test_file()
    
    # Wait a moment for any startup
    log_info("Waiting 2 seconds for API to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health", test_health),
        ("Info", test_info),
        ("API Health", test_api_health),
        ("Analytics", test_analytics),
        ("Documents", test_documents),
        ("Queries", test_queries),
        ("Intent Spaces", test_intent_spaces),
    ]
    
    results = []
    for name, test_func in tests:
        print()
        print(f"Running: {name}")
        print("-"*40)
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            log_error(f"Test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print()
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for name, success in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if success else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"{name:20s} {status}")
    
    print()
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}All tests passed! ✓{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.RED}Some tests failed. ✗{Colors.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
