# Phase 3: Alpaca Paper Trading Integration - Detailed Plan

## 🎯 Goal
Integrate Alpaca Paper Trading API to replace simple trade logging with realistic market simulation using real-time prices and market validation.

---

## 📋 What Changes

### Before (Current):
```
User → Slack → Bot → OMS API → PostgreSQL
                         ↓
                  Logs trade with user-provided data
```

### After (With Alpaca):
```
User → Slack → Bot → OMS API → Alpaca API → Real Market Data
                         ↓
                  PostgreSQL (with Alpaca order ID)
```

---

## 🔧 Components to Modify

| Component | Files | Changes |
|-----------|-------|---------|
| **OMS API** | 6 files | Add Alpaca client, update routes, modify schema |
| **Database** | 1 file | Add columns for Alpaca data |
| **Configuration** | 1 file | Add Alpaca credentials |
| **Dependencies** | 1 file | Add alpaca-trade-api |
| **Documentation** | 3 files | Update guides with Alpaca info |

---

## 📝 Detailed Microsteps

### **Step 1: Prerequisites & Setup** (5 min)
- [ ] 1.1: Create Alpaca account at https://alpaca.markets
- [ ] 1.2: Navigate to Paper Trading section
- [ ] 1.3: Generate API keys (Key ID + Secret Key)
- [ ] 1.4: Save credentials securely (DO NOT commit to git)
- [ ] 1.5: Note the Paper Trading base URL: `https://paper-api.alpaca.markets`

**Verification**: You have 3 values:
- `ALPACA_API_KEY_ID` (looks like: `PKxxxxxxxxxxxxx`)
- `ALPACA_SECRET_KEY` (looks like: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
- `ALPACA_BASE_URL` (exactly: `https://paper-api.alpaca.markets`)

---

### **Step 2: Update Dependencies** (2 min)
- [ ] 2.1: Add `alpaca-trade-api>=3.0.0` to `oms-api/requirements.txt`
- [ ] 2.2: Add `alpaca-trade-api>=3.0.0` to `oms-api/requirements-local.txt`
- [ ] 2.3: Install locally: `pip install alpaca-trade-api`

**Verification**: Run `pip show alpaca-trade-api` - should show version >= 3.0.0

---

### **Step 3: Update Configuration** (3 min)
- [ ] 3.1: Add Alpaca settings to `oms-api/app/config.py`:
  - `alpaca_api_key_id: str`
  - `alpaca_secret_key: str`
  - `alpaca_base_url: str`
  - `use_alpaca: bool = True` (feature flag)
- [ ] 3.2: Add to local `.env`:
  ```
  ALPACA_API_KEY_ID=your_key_id
  ALPACA_SECRET_KEY=your_secret_key
  ALPACA_BASE_URL=https://paper-api.alpaca.markets
  USE_ALPACA=true
  ```
- [ ] 3.3: Verify settings load without errors

**Verification**: Print `settings.alpaca_api_key_id` - should show your key (not "")

---

### **Step 4: Database Schema Update** (5 min)
- [ ] 4.1: Update `oms-api/app/models.py` - add new columns to `Trade` model:
  - `alpaca_order_id: Optional[str]` - Alpaca's order ID
  - `alpaca_filled_price: Optional[float]` - Actual execution price from Alpaca
  - `alpaca_filled_qty: Optional[int]` - Actual filled quantity
  - `alpaca_status: Optional[str]` - Order status (filled, partial_fill, etc.)
  - `alpaca_filled_at: Optional[datetime]` - Alpaca execution timestamp
- [ ] 4.2: For SQLite (local): Schema auto-updates on app restart
- [ ] 4.3: For PostgreSQL (production): Will need migration script

**Verification**: Restart local API - no database errors

---

### **Step 5: Create Alpaca Client** (10 min)
- [ ] 5.1: Create new file `oms-api/app/alpaca_client.py`
- [ ] 5.2: Import `alpaca_trade_api` library
- [ ] 5.3: Create `AlpacaClient` class with methods:
  - `__init__()` - Initialize with API credentials
  - `submit_order()` - Submit market order to Alpaca
  - `get_order()` - Get order status by ID
  - `get_account()` - Get account info (buying power, positions)
  - `get_latest_price()` - Get current stock price
  - `is_market_open()` - Check if market is open
- [ ] 5.4: Add error handling for:
  - Invalid symbols
  - Insufficient buying power
  - Market closed
  - API connection errors
- [ ] 5.5: Add logging for all API calls

**Verification**: Can instantiate `AlpacaClient()` without errors

---

### **Step 6: Update Trade Schemas** (5 min)
- [ ] 6.1: Update `oms-api/app/schemas.py`:
  - Add optional Alpaca fields to `TradeResponse`
  - Add `AlpacaOrderStatus` model
  - Update `TradeExecutionResponse` to include Alpaca data
- [ ] 6.2: Make `gmv` field optional (can be calculated from Alpaca price)
- [ ] 6.3: Add validation for Alpaca-specific scenarios

**Verification**: Schemas import without errors

---

### **Step 7: Update Trade Execution Logic** (15 min)
- [ ] 7.1: Update `oms-api/app/routes.py` - modify `/api/v1/trade` endpoint:
  - Check if `USE_ALPACA` is enabled
  - If enabled:
    - Validate symbol with Alpaca
    - Check if market is open (warn if not)
    - Get current price if GMV not provided
    - Submit order to Alpaca
    - Wait for fill confirmation (with timeout)
    - Use Alpaca's filled price and quantity
    - Store Alpaca order ID
  - If disabled (fallback):
    - Use old logic (simple logging)
- [ ] 7.2: Add error responses for Alpaca failures:
  - 400: Invalid symbol
  - 402: Insufficient buying power
  - 503: Market closed (with market hours info)
  - 503: Alpaca API unavailable
- [ ] 7.3: Update success response to include Alpaca data
- [ ] 7.4: Add logging for all Alpaca interactions

**Verification**: Endpoint still works with `USE_ALPACA=false`

---

### **Step 8: Add Alpaca Health Check** (3 min)
- [ ] 8.1: Update `/health` endpoint in `oms-api/app/main.py`
- [ ] 8.2: Add `alpaca_connected: bool` to health response
- [ ] 8.3: Try to connect to Alpaca account endpoint
- [ ] 8.4: Return connection status

**Verification**: `/health` shows `"alpaca_connected": true` when configured

---

### **Step 9: Update Portfolio Endpoint** (10 min)
- [ ] 9.1: Modify `/api/v1/portfolio/{name}` endpoint
- [ ] 9.2: Add option to fetch live positions from Alpaca
- [ ] 9.3: Compare DB positions vs Alpaca positions
- [ ] 9.4: Include current market value (using latest prices)
- [ ] 9.5: Add P&L calculations (unrealized gains/losses)

**Verification**: Portfolio shows real-time values from Alpaca

---

### **Step 10: Add New Endpoints** (Optional, 15 min)
- [ ] 10.1: `/api/v1/account` - Get Alpaca account info (buying power, equity)
- [ ] 10.2: `/api/v1/quote/{symbol}` - Get current stock quote
- [ ] 10.3: `/api/v1/market-status` - Check if market is open
- [ ] 10.4: `/api/v1/positions` - Get all positions from Alpaca

**Verification**: New endpoints return Alpaca data

---

### **Step 11: Local Testing** (20 min)
- [ ] 11.1: Start local API with Alpaca credentials
- [ ] 11.2: Test `/health` - verify Alpaca connection
- [ ] 11.3: Test trade execution with valid symbol (e.g., AAPL)
- [ ] 11.4: Verify Alpaca order ID in response
- [ ] 11.5: Check database - Alpaca fields populated
- [ ] 11.6: Test invalid symbol - should get 400 error
- [ ] 11.7: Test when market closed - should get warning/error
- [ ] 11.8: Test portfolio endpoint - verify real prices
- [ ] 11.9: Check Alpaca dashboard - verify order appears
- [ ] 11.10: Test with `USE_ALPACA=false` - verify fallback works

**Verification**: All local tests pass

---

### **Step 12: Update Test Suite** (15 min)
- [ ] 12.1: Update `oms-api/test_api.py`
- [ ] 12.2: Add mock for Alpaca API calls
- [ ] 12.3: Test Alpaca integration paths
- [ ] 12.4: Test error scenarios (invalid symbol, market closed)
- [ ] 12.5: Test fallback mode (USE_ALPACA=false)
- [ ] 12.6: Run full test suite - ensure all pass

**Verification**: `python test_api.py` - all tests pass

---

### **Step 13: Update Slack Bot** (10 min)
- [ ] 13.1: Update confirmation message in `slack-bot/app/blocks.py`
- [ ] 13.2: Add Alpaca-specific fields to confirmation:
  - Alpaca Order ID
  - Actual filled price
  - Actual filled quantity
  - Market status at execution
- [ ] 13.3: Update error messages for Alpaca-specific errors
- [ ] 13.4: Add market hours warning in modal (if closed)

**Verification**: Slack confirmation shows Alpaca data

---

### **Step 14: Production Deployment - OMS API** (10 min)
- [ ] 14.1: Go to Render dashboard → slackoms-api service
- [ ] 14.2: Add environment variables:
  - `ALPACA_API_KEY_ID` = your_key_id
  - `ALPACA_SECRET_KEY` = your_secret_key
  - `ALPACA_BASE_URL` = https://paper-api.alpaca.markets
  - `USE_ALPACA` = true
- [ ] 14.3: Click "Save Changes"
- [ ] 14.4: Service will auto-deploy
- [ ] 14.5: Wait for deployment to complete (~3 min)

**Verification**: Check `/health` - `"alpaca_connected": true`

---

### **Step 15: Production Deployment - Slack Bot** (5 min)
- [ ] 15.1: Commit and push Slack bot changes to GitHub
- [ ] 15.2: Render auto-deploys the bot
- [ ] 15.3: Wait for deployment (~2 min)

**Verification**: Bot health check shows updated version

---

### **Step 16: Database Migration (PostgreSQL)** (10 min)
- [ ] 16.1: Create Alembic migration file for new columns
- [ ] 16.2: OR use SQLAlchemy's `create_all()` if columns auto-add
- [ ] 16.3: Verify new columns exist in production database
- [ ] 16.4: Existing trades have NULL for new Alpaca fields (expected)

**Verification**: Query database - new columns present

---

### **Step 17: Production Testing** (15 min)
- [ ] 17.1: Wake up both services (hit /health endpoints)
- [ ] 17.2: In Slack, execute test trade: `/trade AAPL`
- [ ] 17.3: Fill modal with test values
- [ ] 17.4: Submit trade
- [ ] 17.5: Verify confirmation shows Alpaca Order ID
- [ ] 17.6: Check Alpaca dashboard - order appears
- [ ] 17.7: Check production database - Alpaca fields populated
- [ ] 17.8: Test invalid symbol - verify error message
- [ ] 17.9: Test portfolio endpoint - verify real prices

**Verification**: End-to-end Alpaca integration working in production

---

### **Step 18: Documentation Updates** (15 min)
- [ ] 18.1: Update `README.md` - add Alpaca integration section
- [ ] 18.2: Update `oms-api/DEPLOYMENT.md` - add Alpaca env vars
- [ ] 18.3: Update `QUICKSTART.md` - add Alpaca setup steps
- [ ] 18.4: Create `ALPACA_SETUP.md` - detailed Alpaca guide
- [ ] 18.5: Update `PROJECT_SUMMARY.md` - add Phase 3
- [ ] 18.6: Add code comments explaining Alpaca integration

**Verification**: Documentation is clear and complete

---

### **Step 19: Git Commit & Push** (5 min)
- [ ] 19.1: Stage all changes: `git add .`
- [ ] 19.2: Commit: `git commit -m "Phase 3: Add Alpaca Paper Trading integration"`
- [ ] 19.3: Push to GitHub: `git push origin main`
- [ ] 19.4: Verify Render auto-deploys

**Verification**: GitHub shows latest commit, Render deploys successfully

---

### **Step 20: Final Verification** (10 min)
- [ ] 20.1: Test complete trade flow via Slack
- [ ] 20.2: Verify Alpaca dashboard shows order
- [ ] 20.3: Check database has complete data
- [ ] 20.4: Test portfolio with real prices
- [ ] 20.5: Verify all documentation is accurate
- [ ] 20.6: Test error scenarios
- [ ] 20.7: Mark Phase 3 as complete

**Verification**: Full end-to-end system working with Alpaca

---

## ⚠️ Potential Issues & Solutions

### Issue 1: Market Closed
**Problem**: Alpaca rejects orders when market is closed  
**Solution**: 
- Add market hours check before showing modal
- Allow submission but show warning
- Enable extended hours trading if needed

### Issue 2: Insufficient Buying Power
**Problem**: Alpaca account has limited paper money  
**Solution**:
- Check buying power before order
- Show clear error message
- Alpaca paper accounts typically start with $100,000

### Issue 3: Invalid Symbol
**Problem**: User enters non-existent ticker  
**Solution**:
- Alpaca validates symbols automatically
- Return 400 error with clear message
- Consider adding symbol search/autocomplete later

### Issue 4: Alpaca API Rate Limits
**Problem**: Too many requests to Alpaca  
**Solution**:
- Alpaca paper trading: 200 req/min (generous)
- Add rate limiting on our side if needed
- Cache stock prices (refresh every 15 sec)

### Issue 5: Database Migration
**Problem**: Adding columns to existing database  
**Solution**:
- New columns are nullable
- Existing trades unaffected
- Future trades have Alpaca data

### Issue 6: Alpaca API Down
**Problem**: Alpaca service unavailable  
**Solution**:
- Set `USE_ALPACA=false` to fall back to old logic
- Add health check monitoring
- Show meaningful error to users

---

## 🎯 Success Criteria

- [ ] ✅ Can execute trades via Alpaca API
- [ ] ✅ Trades use real market prices
- [ ] ✅ Alpaca order IDs stored in database
- [ ] ✅ Portfolio shows real-time values
- [ ] ✅ Market validation working (invalid symbols rejected)
- [ ] ✅ Error handling for all Alpaca scenarios
- [ ] ✅ Slack bot shows Alpaca data in confirmations
- [ ] ✅ Health checks include Alpaca status
- [ ] ✅ Documentation updated
- [ ] ✅ All tests passing

---

## 📊 Estimated Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Prerequisites | 5 min | Create Alpaca account |
| Code Changes | 60-90 min | Client, routes, schemas, testing |
| Local Testing | 20 min | Verify all functionality |
| Deployment | 15 min | Update Render services |
| Production Testing | 15 min | End-to-end verification |
| Documentation | 15 min | Update all docs |
| **TOTAL** | **~2-3 hours** | With breaks |

---

## 🚀 Ready to Start?

**Switch to agent mode and say**: "Let's start Phase 3, begin with Step 1"

I'll guide you through each microstep and verify completion before moving to the next.

---

*Last Updated: October 16, 2025*  
*Status: Planning Complete - Ready to Execute*

