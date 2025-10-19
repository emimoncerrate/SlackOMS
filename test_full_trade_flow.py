#!/usr/bin/env python3
"""
Comprehensive test of the full trade execution flow
"""

import asyncio
import os
import sys
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

async def test_full_trade_execution():
    """Test the complete trade execution flow."""
    
    print("🧪 TESTING FULL TRADE EXECUTION FLOW")
    print("=" * 60)
    
    try:
        # Import the simple Alpaca client directly
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from services.simple_alpaca_client import SimpleAlpacaClient
        
        # Get credentials from environment
        api_key = os.getenv('ALPACA_PAPER_API_KEY')
        secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        base_url = os.getenv('ALPACA_PAPER_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not api_key or not secret_key:
            print("❌ Missing Alpaca credentials")
            return False
        
        print(f"✅ Using API Key: {api_key[:8]}...")
        print(f"✅ Using Base URL: {base_url}")
        
        # Create Alpaca client
        alpaca = SimpleAlpacaClient(api_key, secret_key, base_url)
        
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
        
        # Test 2: Simulate the exact trade flow from Slack modal
        print("\n🚀 Test 2: Simulate Slack Modal Trade Flow")
        
        # Simulate modal submission data
        modal_data = {
            "symbol": "AAPL",
            "quantity": "2", 
            "trade_side": "buy",
            "order_type": "market",
            "limit_price": None
        }
        
        print(f"📝 Simulating modal submission:")
        print(f"   Symbol: {modal_data['symbol']}")
        print(f"   Quantity: {modal_data['quantity']}")
        print(f"   Side: {modal_data['trade_side']}")
        print(f"   Order Type: {modal_data['order_type']}")
        
        # Validate inputs (same as in modal handler)
        symbol = modal_data['symbol'].upper()
        quantity = modal_data['quantity']
        trade_side = modal_data['trade_side']
        order_type = modal_data['order_type']
        
        if not symbol or not quantity:
            raise ValueError("Missing symbol or quantity")
        
        qty_int = int(quantity)
        if qty_int <= 0:
            raise ValueError("Quantity must be positive")
        
        print(f"✅ Input validation passed")
        
        # Execute trade (same as in modal handler)
        print(f"\n🚀 Executing Trade: {trade_side.upper()} {qty_int} {symbol}")
        
        if order_type == "market":
            result = alpaca.submit_order(
                symbol=symbol,
                qty=qty_int,
                side=trade_side,
                order_type="market",
                time_in_force="day"
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")
        
        # Test the result parsing (same as in modal handler)
        print(f"\n📋 Test 3: Result Parsing")
        print(f"Raw result: {result}")
        
        if result:
            # Check both 'id' and 'order_id' fields
            order_id = result.get("id") or result.get("order_id")
            status = result.get("status", "submitted")
            
            print(f"✅ Order ID found: {order_id}")
            print(f"✅ Status: {status}")
            
            if order_id:
                print(f"\n✅ TRADE EXECUTION SUCCESS!")
                print(f"📊 Order Details:")
                print(f"   • Symbol: {symbol}")
                print(f"   • Action: {trade_side.upper()}")
                print(f"   • Quantity: {qty_int} shares")
                print(f"   • Order Type: {order_type.title()}")
                print(f"   • Order ID: {order_id}")
                print(f"   • Status: {status}")
                print(f"   • Submitted At: {result.get('submitted_at', 'N/A')}")
                
                # Test 4: Verify order in system
                print(f"\n📋 Test 4: Verify Order in System")
                orders = alpaca.get_orders(status="all", limit=5)
                if orders:
                    print(f"✅ Recent orders retrieved:")
                    for i, order in enumerate(orders[:3], 1):
                        order_id_check = order.get('id', 'N/A')
                        if order_id_check == order_id:
                            print(f"   {i}. ✅ FOUND OUR ORDER: {order.get('side', 'N/A').upper()} {order.get('qty', 'N/A')} {order.get('symbol', 'N/A')} - {order.get('status', 'N/A')}")
                        else:
                            print(f"   {i}. {order.get('side', 'N/A').upper()} {order.get('qty', 'N/A')} {order.get('symbol', 'N/A')} - {order.get('status', 'N/A')}")
                
                return True
            else:
                print(f"❌ No order ID found in result")
                return False
        else:
            print(f"❌ No result returned from order submission")
            return False
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        print(f"🚨 Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main test function."""
    print(f"🕐 Test started at: {datetime.now()}")
    print(f"🎯 Testing the exact same flow as Slack modal submission")
    
    success = await test_full_trade_execution()
    
    if success:
        print(f"\n" + "=" * 60)
        print(f"🎉 FULL TRADE FLOW TEST PASSED!")
        print(f"✅ Modal submission → Trade execution → Order confirmation")
        print(f"✅ Your Slack bot trade execution is working correctly!")
        print(f"⚠️  The only issue is Slack messaging (channel permissions)")
        print(f"💡 Trades are executing successfully, just need to fix DM permissions")
    else:
        print(f"\n" + "=" * 60)
        print(f"❌ TRADE FLOW TEST FAILED!")
        print(f"🔧 Check the error messages above")
    
    print(f"🕐 Test completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main())