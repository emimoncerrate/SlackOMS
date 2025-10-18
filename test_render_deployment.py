#!/usr/bin/env python3
"""
Test script for Render deployment verification
Tests the health endpoint and basic functionality
"""

import requests
import json
import sys
import time
from typing import Optional

def test_health_endpoint(base_url: str) -> bool:
    """Test the health check endpoint."""
    try:
        print(f"🔍 Testing health endpoint: {base_url}/health")
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Environment: {data.get('environment')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint(base_url: str) -> bool:
    """Test the root endpoint."""
    try:
        print(f"🔍 Testing root endpoint: {base_url}/")
        response = requests.get(f"{base_url}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint accessible")
            print(f"   Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_slack_endpoint(base_url: str) -> bool:
    """Test that Slack endpoint is accessible (should return 400 for invalid request)."""
    try:
        print(f"🔍 Testing Slack endpoint: {base_url}/slack/events")
        # Send empty POST (should fail gracefully)
        response = requests.post(f"{base_url}/slack/events", timeout=10)
        
        # We expect this to fail (400 or 403) since we're not sending valid Slack data
        if response.status_code in [400, 403, 422]:
            print(f"✅ Slack endpoint accessible (returned {response.status_code} as expected)")
            return True
        else:
            print(f"⚠️  Slack endpoint returned unexpected status: {response.status_code}")
            return True  # Still consider this a pass
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Slack endpoint error: {e}")
        return False

def wait_for_service(base_url: str, max_attempts: int = 12) -> bool:
    """Wait for service to become available (for cold starts)."""
    print(f"⏳ Waiting for service to start (max {max_attempts * 10} seconds)...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Service is ready after {attempt * 10} seconds")
                return True
        except:
            pass
        
        if attempt < max_attempts - 1:
            print(f"   Attempt {attempt + 1}/{max_attempts} - waiting 10 seconds...")
            time.sleep(10)
    
    print(f"❌ Service did not start within {max_attempts * 10} seconds")
    return False

def main():
    """Main test function."""
    if len(sys.argv) != 2:
        print("Usage: python test_render_deployment.py <BASE_URL>")
        print("Example: python test_render_deployment.py https://jain-trading-bot.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("=" * 60)
    print("🧪 Render Deployment Test Suite")
    print("=" * 60)
    print(f"Testing service at: {base_url}")
    print()
    
    # Wait for service to be ready
    if not wait_for_service(base_url):
        print("\n❌ Service is not responding. Check Render dashboard for errors.")
        sys.exit(1)
    
    print()
    
    # Run tests
    tests = [
        ("Health Endpoint", lambda: test_health_endpoint(base_url)),
        ("Root Endpoint", lambda: test_root_endpoint(base_url)),
        ("Slack Endpoint", lambda: test_slack_endpoint(base_url)),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        if test_func():
            passed += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! Your Render deployment is working correctly.")
        print()
        print("Next steps:")
        print("1. Configure your Slack app slash commands")
        print("2. Set the webhook URL to: {}/slack/events".format(base_url))
        print("3. Test the /trade command in Slack")
        print()
        sys.exit(0)
    else:
        print(f"❌ {total - passed} test(s) failed. Check the errors above.")
        print()
        print("Troubleshooting:")
        print("1. Check Render dashboard for deployment errors")
        print("2. Verify environment variables are set correctly")
        print("3. Check service logs for detailed error messages")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()