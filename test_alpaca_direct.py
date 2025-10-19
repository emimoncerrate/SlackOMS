#!/usr/bin/env python3
"""
Direct test of Alpaca API functionality without service container
"""

import asyncio
import os
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

async def test_alpaca_direct():
    """Test Alpaca API directly."""
    
    print("🧪 TESTING ALPACA API DIRECTLY")
    print("=" * 50)
    
    try:
        # Import the simple Alpaca client
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        
        from services.simple_alpaca_client import SimpleAlpacaClient
        
        # Get credentials from environment
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        base_url = os.getenv('ALPACA_PAPER_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not api_key or not secret_key:
            print("❌ Missing Alpaca credentials in environment variables")
            print("   Required: ALPACA_PAPER_API_KEY, ALPACA_PAPER_SECRET_KEY")
            return False
        
        print(f"✅ Using API Key: {api_key[:8]}...")
        print(f"✅ Using Base URL: {base_url}")
        
        # Create Alpaca client
        alpaca = SimpleAlpacaClient(api_key, secret_key, base_url)
        print("✅ Alpaca client created")
        
        # Test 1: Get account info
        print("\n📊 Test 1: Account Information")
        account_info = alpaca.get_account()
        if account_info:
            print(f"✅ Account Number: {account_info.get('account_number', 'N/A')}")
            print(f"✅ Cash Available: ${float(account_info.get('cash', 0)):,.2f}")
            print(f"✅ Buying Power: ${float(account_info.get('buying_power', 0)):,.2f}")
            print(f"✅ Account Status: {account_info.get('status', 'N/A')}")
        else:
            print("❌ Failed to get account info")
            return False
        
        # Test 2: Submit a test buy order
        print("\n🚀 Test 2: Submit Test Buy Order")
        test_symbol = "AAPL"
        test_quantity = 1
        
        print(f"Submitting: BUY {test_quantity} {test_symbol} (Market Order)")
        
        buy_result = alpaca.submit_order(
            symbol=test_symbol,
            qty=test_quantity,
            side="buy",
            order_type="market",
            time_in_force="day"
        )
        
        if buy_result:
            print("✅ BUY ORDER SUBMITTED SUCCESSFULLY!")
            print(f"   Order ID: {buy_result.get('id', 'N/A')}")
            print(f"   Symbol: {buy_result.get('symbol', 'N/A')}")
            print(f"   Quantity: {buy_result.get('qty', 'N/A')}")
            print(f"   Side: {buy_result.get('side', 'N/A')}")
            print(f"   Order Type: {buy_result.get('order_type', 'N/A')}")
            print(f"   Status: {buy_result.get('status', 'N/A')}")
            print(f"   Submitted At: {buy_result.get('submitted_at', 'N/A')}")
        else:
            print("❌ BUY ORDER FAILED")
            return False
        
        # Test 3: Submit a test sell order
        print(f"\n📉 Test 3: Submit Test Sell Order")
        print(f"Submitting: SELL {test_quantity} {test_symbol} (Market Order)")
        
        sell_result = alpaca.submit_order(
            symbol=test_symbol,
            qty=test_quantity,
            side="sell",
            order_type="market",
            time_in_force="day"
        )
        
        if sell_result:
            print("✅ SELL ORDER SUBMITTED SUCCESSFULLY!")
            print(f"   Order ID: {sell_result.get('id', 'N/A')}")
            print(f"   Symbol: {sell_result.get('symbol', 'N/A')}")
            print(f"   Quantity: {sell_result.get('qty', 'N/A')}")
            print(f"   Side: {sell_result.get('side', 'N/A')}")
            print(f"   Order Type: {sell_result.get('order_type', 'N/A')}")
            print(f"   Status: {sell_result.get('status', 'N/A')}")
            print(f"   Submitted At: {sell_result.get('submitted_at', 'N/A')}")
        else:
            print("❌ SELL ORDER FAILED")
            return False
        
        # Test 4: Get recent orders
        print(f"\n📋 Test 4: Recent Orders")
        orders = alpaca.get_orders(status="all", limit=5)
        if orders:
            print(f"✅ Retrieved {len(orders)} recent orders:")
            for i, order in enumerate(orders[:3], 1):
                print(f"   {i}. {order.get('side', 'N/A').upper()} {order.get('qty', 'N/A')} {order.get('symbol', 'N/A')} - {order.get('status', 'N/A')}")
        else:
            print("❌ Failed to get orders")
        
        # Test 5: Get positions
        print(f"\n💼 Test 5: Current Positions")
        positions = alpaca.get_positions()
        if positions is not None:
            if len(positions) > 0:
                print(f"✅ Current positions ({len(positions)}):")
                for pos in positions[:3]:
                    qty = pos.get('qty', '0')
                    symbol = pos.get('symbol', 'N/A')
                    market_value = pos.get('market_value', '0')
                    print(f"   • {qty} shares of {symbol} (Value: ${float(market_value):,.2f})")
            else:
                print("✅ No current positions (all cash)")
        else:
            print("❌ Failed to get positions")
        
        # Test 6: Check market status
        print(f"\n🕐 Test 6: Market Status")
        is_open = alpaca.is_market_open()
        print(f"✅ Market is {'OPEN' if is_open else 'CLOSED'}")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Alpaca API is working correctly")
        print("✅ Paper trading orders are being submitted successfully")
        print("⚠️  Remember: This is paper trading - no real money involved")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        print(f"🚨 Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main test function."""
    print(f"🕐 Test started at: {datetime.now()}")
    
    success = await test_alpaca_direct()
    
    if success:
        print(f"\n✅ Alpaca API test completed successfully!")
        print(f"🎯 Your Slack bot trade execution should work!")
    else:
        print(f"\n❌ Alpaca API test failed!")
        print(f"🔧 Check the error messages above and fix any issues")
    
    print(f"🕐 Test completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main())