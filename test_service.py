#!/usr/bin/env python3
"""
Quick test script to check if the service is responding
"""

import requests
import json

def test_service():
    """Test the live service endpoints."""
    
    base_url = "https://slackoms.onrender.com"
    
    endpoints = [
        "/",
        "/health", 
        "/ready"
    ]
    
    print("🔍 Testing SlackOMS service endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 Testing: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ JSON Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   📝 Text Response: {response.text[:200]}...")
            else:
                print(f"   ❌ Error Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout - Service might be starting up")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection Error - Service might be down")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Testing Slack challenge endpoint...")
    
    # Test Slack challenge
    challenge_url = f"{base_url}/slack/events"
    challenge_data = {
        "type": "url_verification",
        "challenge": "test123"
    }
    
    try:
        response = requests.post(
            challenge_url, 
            json=challenge_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Challenge Response: {response.json()}")
        else:
            print(f"   ❌ Challenge Failed: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Challenge Error: {e}")

if __name__ == "__main__":
    test_service()