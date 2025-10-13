#!/usr/bin/env python3
"""
Test script for OMS API
Tests basic functionality without needing Postman
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("TEST_API_URL", "http://localhost:8000")
API_KEY = os.getenv("OMS_API_KEY")

def test_health_check():
    """Test health check endpoint (no auth required)"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, "Health check failed"
    print("✅ PASSED")


def test_missing_api_key():
    """Test that requests without API key are rejected"""
    print("\n" + "="*60)
    print("TEST 2: Missing API Key (should fail)")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/api/v1/trade",
        json={
            "symbol": "AAPL",
            "quantity": 100,
            "gmv": 17500.00,
            "side": "BUY",
            "portfolio_name": "Test",
            "user_id": "U123"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 401, "Should return 401 Unauthorized"
    print("✅ PASSED")


def test_invalid_api_key():
    """Test that requests with invalid API key are rejected"""
    print("\n" + "="*60)
    print("TEST 3: Invalid API Key (should fail)")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/api/v1/trade",
        headers={"X-API-Key": "invalid-key-12345"},
        json={
            "symbol": "AAPL",
            "quantity": 100,
            "gmv": 17500.00,
            "side": "BUY",
            "portfolio_name": "Test",
            "user_id": "U123"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 401, "Should return 401 Unauthorized"
    print("✅ PASSED")


def test_valid_trade_execution():
    """Test successful trade execution with valid API key"""
    print("\n" + "="*60)
    print("TEST 4: Valid Trade Execution (should succeed)")
    print("="*60)
    
    if not API_KEY:
        print("⚠️  SKIPPED: No API_KEY found in environment")
        return None
    
    trade_data = {
        "symbol": "MSFT",
        "quantity": 50,
        "gmv": 17500.00,
        "side": "BUY",
        "portfolio_name": "Tech Portfolio",
        "user_id": "U123TEST"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/trade",
        headers={"X-API-Key": API_KEY},
        json=trade_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 201, "Trade execution failed"
    assert "trade_id" in response.json(), "No trade_id in response"
    print("✅ PASSED")
    
    return response.json()["trade_id"]


def test_list_trades(trade_id=None):
    """Test listing trades"""
    print("\n" + "="*60)
    print("TEST 5: List Trades")
    print("="*60)
    
    if not API_KEY:
        print("⚠️  SKIPPED: No API_KEY found in environment")
        return
    
    response = requests.get(
        f"{BASE_URL}/api/v1/trades",
        headers={"X-API-Key": API_KEY},
        params={"limit": 5}
    )
    
    print(f"Status Code: {response.status_code}")
    trades = response.json()
    print(f"Number of trades returned: {len(trades)}")
    
    if trades:
        print(f"Most recent trade: {json.dumps(trades[0], indent=2)}")
    
    assert response.status_code == 200, "Failed to list trades"
    print("✅ PASSED")


def test_get_specific_trade(trade_id):
    """Test getting a specific trade by ID"""
    print("\n" + "="*60)
    print(f"TEST 6: Get Specific Trade ({trade_id})")
    print("="*60)
    
    if not API_KEY or not trade_id:
        print("⚠️  SKIPPED: No API_KEY or trade_id")
        return
    
    response = requests.get(
        f"{BASE_URL}/api/v1/trades/{trade_id}",
        headers={"X-API-Key": API_KEY}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, "Failed to get trade"
    print("✅ PASSED")


def test_get_portfolio():
    """Test getting portfolio summary"""
    print("\n" + "="*60)
    print("TEST 7: Get Portfolio Summary")
    print("="*60)
    
    if not API_KEY:
        print("⚠️  SKIPPED: No API_KEY found in environment")
        return
    
    response = requests.get(
        f"{BASE_URL}/api/v1/portfolio/Tech Portfolio",
        headers={"X-API-Key": API_KEY}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200, "Failed to get portfolio"
    print("✅ PASSED")


def test_invalid_trade_data():
    """Test validation with invalid data"""
    print("\n" + "="*60)
    print("TEST 8: Invalid Trade Data (should fail)")
    print("="*60)
    
    if not API_KEY:
        print("⚠️  SKIPPED: No API_KEY found in environment")
        return
    
    # Negative quantity should fail
    response = requests.post(
        f"{BASE_URL}/api/v1/trade",
        headers={"X-API-Key": API_KEY},
        json={
            "symbol": "AAPL",
            "quantity": -100,  # Invalid!
            "gmv": 17500.00,
            "side": "BUY",
            "portfolio_name": "Test",
            "user_id": "U123"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code in [400, 422], "Should reject invalid data"
    print("✅ PASSED")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OMS API TEST SUITE")
    print("="*60)
    print(f"Testing API at: {BASE_URL}")
    print(f"API Key configured: {'Yes' if API_KEY else 'No'}")
    
    try:
        # Run tests
        test_health_check()
        test_missing_api_key()
        test_invalid_api_key()
        trade_id = test_valid_trade_execution()
        test_list_trades(trade_id)
        if trade_id:
            test_get_specific_trade(trade_id)
        test_get_portfolio()
        test_invalid_trade_data()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        
    except AssertionError as e:
        print("\n" + "="*60)
        print(f"❌ TEST FAILED: {str(e)}")
        print("="*60)
        return 1
    except requests.exceptions.ConnectionError:
        print("\n" + "="*60)
        print(f"❌ CONNECTION ERROR: Could not connect to {BASE_URL}")
        print("Make sure the API server is running!")
        print("="*60)
        return 1
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        print("="*60)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

