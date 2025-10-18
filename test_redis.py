#!/usr/bin/env python3
"""
Redis Connection Test Script
Run this to verify Redis is working properly
"""

import os
import redis
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_redis_connection():
    """Test Redis connection and basic operations."""
    
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    redis_enabled = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'
    
    print("🔍 Testing Redis Configuration...")
    print(f"Redis URL: {redis_url}")
    print(f"Redis Enabled: {redis_enabled}")
    print()
    
    if not redis_enabled:
        print("⚠️  Redis is disabled in configuration")
        return False
    
    try:
        # Connect to Redis
        print("🔌 Connecting to Redis...")
        r = redis.from_url(redis_url, decode_responses=True)
        
        # Test connection
        print("📡 Testing connection...")
        r.ping()
        print("✅ Redis connection successful!")
        
        # Test basic operations
        print("🧪 Testing basic operations...")
        
        # Set a test value
        r.set("test_key", "Hello Redis!", ex=60)  # Expires in 60 seconds
        print("✅ Set operation successful")
        
        # Get the test value
        value = r.get("test_key")
        print(f"✅ Get operation successful: {value}")
        
        # Test hash operations (used by the bot)
        r.hset("test_hash", mapping={
            "field1": "value1",
            "field2": "value2",
            "timestamp": "2024-01-01T00:00:00Z"
        })
        print("✅ Hash set operation successful")
        
        # Get hash values
        hash_data = r.hgetall("test_hash")
        print(f"✅ Hash get operation successful: {hash_data}")
        
        # Test expiration
        r.expire("test_hash", 60)  # Expires in 60 seconds
        ttl = r.ttl("test_hash")
        print(f"✅ Expiration set successfully: {ttl} seconds remaining")
        
        # Clean up test data
        r.delete("test_key", "test_hash")
        print("✅ Cleanup successful")
        
        # Get Redis info
        info = r.info()
        print(f"\n📊 Redis Info:")
        print(f"   Version: {info.get('redis_version', 'Unknown')}")
        print(f"   Memory Used: {info.get('used_memory_human', 'Unknown')}")
        print(f"   Connected Clients: {info.get('connected_clients', 'Unknown')}")
        print(f"   Total Commands: {info.get('total_commands_processed', 'Unknown')}")
        
        print("\n🎉 Redis is working perfectly!")
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        print("\n💡 Possible solutions:")
        print("1. Make sure Redis is running")
        print("2. Check the REDIS_URL in your .env file")
        print("3. On Render, make sure the Redis service is created and linked")
        return False
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

def show_redis_benefits():
    """Show what Redis provides for the trading bot."""
    
    print("\n" + "="*60)
    print("🚀 REDIS BENEFITS FOR YOUR TRADING BOT")
    print("="*60)
    print()
    print("📈 Performance Improvements:")
    print("   • Market data caching (faster price lookups)")
    print("   • User session management")
    print("   • Rate limiting and throttling")
    print("   • Frequently accessed data caching")
    print()
    print("💰 Cost Savings:")
    print("   • Reduces API calls to Finnhub (saves on rate limits)")
    print("   • Reduces database queries")
    print("   • Faster response times = better user experience")
    print()
    print("🔒 Features Enabled:")
    print("   • Advanced rate limiting per user")
    print("   • Session-based authentication")
    print("   • Real-time market data caching")
    print("   • Trade execution queue management")
    print()
    print("📊 What Gets Cached:")
    print("   • Stock prices (5-minute cache)")
    print("   • User permissions and roles")
    print("   • Market data and company info")
    print("   • Trading session data")
    print("="*60)

if __name__ == "__main__":
    success = test_redis_connection()
    show_redis_benefits()
    
    if success:
        print("\n✅ Your Redis setup is ready for the trading bot!")
    else:
        print("\n⚠️  Redis setup needs attention, but the bot will work with memory cache")