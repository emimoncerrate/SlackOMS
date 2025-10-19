# Phase 3: Alpaca Integration + Multi-User System - UPDATED PLAN

## 🎯 Goals
1. Integrate Alpaca Paper Trading API for realistic market simulation
2. Implement multi-user system with role-based access control
3. Add personal + shared portfolio management
4. Enable admin management via Slack commands

---

## 📋 What We're Building

### New Capabilities:
- ✅ Real-time stock prices from Alpaca
- ✅ Market validation (invalid symbols rejected)
- ✅ User management (5-person team)
- ✅ Role-based permissions (admin, trader, analyst, viewer)
- ✅ Personal + shared portfolios
- ✅ Portfolio access control
- ✅ Admin commands in Slack
- ✅ User-aware trade execution

---

## 🗄️ Database Changes

### New Tables:
1. **users** - Team members
2. **roles** - Permission templates
3. **portfolios** - Both personal and shared
4. **portfolio_access** - Who can access what

### Updated Tables:
1. **trades** - Add user_id, portfolio_id, Alpaca fields

---

## 📝 DETAILED MICROSTEPS (Estimated: 3-4 hours)

---

### **STEP 0: Prerequisites & Planning** (10 min)

#### 0.1: Create Alpaca Account
- [ ] Go to https://alpaca.markets
- [ ] Sign up (free account)
- [ ] Navigate to Paper Trading section
- [ ] Click "Generate API Keys"
- [ ] Copy and save (don't commit to git!):
  - `API Key ID` (starts with PK...)
  - `Secret Key` (long string)

#### 0.2: Verify Alpaca Account
- [ ] Login to Alpaca dashboard
- [ ] Verify paper trading account shows $100,000
- [ ] Note the URL: https://paper-api.alpaca.markets

#### 0.3: Plan User Roles
- [ ] Identify your 5 team members
- [ ] Assign roles:
  - 1 Admin (you)
  - 2-3 Traders
  - 0-1 Analyst
  - 0-1 Viewer
- [ ] Note their Slack user IDs (will get from first use)

**Verification**: You have Alpaca credentials saved securely

---

### **STEP 1: Update Dependencies** (5 min)

#### 1.1: Add Alpaca Library to Production
- [ ] Open `oms-api/requirements.txt`
- [ ] Add line: `alpaca-trade-api>=3.0.0`
- [ ] Save file

#### 1.2: Add Alpaca Library to Local Dev
- [ ] Open `oms-api/requirements-local.txt`
- [ ] Add line: `alpaca-trade-api>=3.0.0`
- [ ] Save file

#### 1.3: Install Locally
- [ ] Run: `cd oms-api && source venv/bin/activate`
- [ ] Run: `pip install alpaca-trade-api`
- [ ] Verify: `pip show alpaca-trade-api` (should show version 3.x.x)

**Verification**: `pip list | grep alpaca` shows the package

---

### **STEP 2: Update Configuration** (10 min)

#### 2.1: Add Alpaca Settings to Config
- [ ] Open `oms-api/app/config.py`
- [ ] Add to `Settings` class:
  ```python
  # Alpaca Configuration
  alpaca_api_key_id: str = ""
  alpaca_secret_key: str = ""
  alpaca_base_url: str = "https://paper-api.alpaca.markets"
  use_alpaca: bool = True
  ```

#### 2.2: Update Local Environment File
- [ ] Open `oms-api/.env`
- [ ] Add these lines (replace with your actual keys):
  ```
  ALPACA_API_KEY_ID=PKxxxxxxxxxxxxx
  ALPACA_SECRET_KEY=your_secret_key_here
  ALPACA_BASE_URL=https://paper-api.alpaca.markets
  USE_ALPACA=true
  ```

#### 2.3: Test Configuration Loading
- [ ] Start local API: `cd oms-api && source venv/bin/activate && uvicorn app.main:app --reload`
- [ ] Check logs - no config errors
- [ ] Stop server (Ctrl+C)

**Verification**: API starts without errors, settings loaded

---

### **STEP 3: Create Database Models - Part 1 (Users & Roles)** (15 min)

#### 3.1: Create User and Role Models
- [ ] Open `oms-api/app/models.py`
- [ ] Add after existing imports:
  ```python
  from sqlalchemy import Boolean, ForeignKey
  from sqlalchemy.orm import relationship
  ```
- [ ] Add at the end of file (before Trade model or after):
  ```python
  class Role(Base):
      __tablename__ = "roles"
      
      id = Column(Integer, primary_key=True, index=True)
      name = Column(String(50), unique=True, nullable=False)
      description = Column(String(255))
      
      # Permissions
      can_create_trade = Column(Boolean, default=False)
      can_view_all_trades = Column(Boolean, default=False)
      can_manage_portfolios = Column(Boolean, default=False)
      max_trade_value = Column(Numeric(15, 2), nullable=True)
      
      created_at = Column(DateTime, default=datetime.utcnow)
  
  class User(Base):
      __tablename__ = "users"
      
      id = Column(Integer, primary_key=True, index=True)
      slack_user_id = Column(String(50), unique=True, nullable=False, index=True)
      name = Column(String(100), nullable=False)
      email = Column(String(100), nullable=True)
      role = Column(String(50), nullable=False, default="viewer")
      is_active = Column(Boolean, default=True)
      
      created_at = Column(DateTime, default=datetime.utcnow)
      
      # Relationships
      trades = relationship("Trade", back_populates="user")
      portfolio_access = relationship("PortfolioAccess", back_populates="user")
  ```

#### 3.2: Save and Verify
- [ ] Save `models.py`
- [ ] Check for syntax errors (imports, indentation)

**Verification**: File saved, no obvious syntax errors

---

### **STEP 4: Create Database Models - Part 2 (Portfolios)** (15 min)

#### 4.1: Add Portfolio Models
- [ ] Still in `oms-api/app/models.py`
- [ ] Add these models:
  ```python
  class Portfolio(Base):
      __tablename__ = "portfolios"
      
      id = Column(Integer, primary_key=True, index=True)
      name = Column(String(100), unique=True, nullable=False, index=True)
      type = Column(String(20), nullable=False)  # 'personal' or 'shared'
      owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
      description = Column(String(255), nullable=True)
      
      created_at = Column(DateTime, default=datetime.utcnow)
      
      # Relationships
      owner = relationship("User", foreign_keys=[owner_id])
      access_grants = relationship("PortfolioAccess", back_populates="portfolio")
      trades = relationship("Trade", back_populates="portfolio")
  
  class PortfolioAccess(Base):
      __tablename__ = "portfolio_access"
      
      id = Column(Integer, primary_key=True, index=True)
      portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
      user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
      access_level = Column(String(20), nullable=False)  # 'view', 'trade', 'admin'
      
      created_at = Column(DateTime, default=datetime.utcnow)
      
      # Relationships
      portfolio = relationship("Portfolio", back_populates="access_grants")
      user = relationship("User", back_populates="portfolio_access")
      
      # Unique constraint
      __table_args__ = (
          UniqueConstraint('portfolio_id', 'user_id', name='_portfolio_user_uc'),
      )
  ```

#### 4.2: Update Trade Model
- [ ] Find the `Trade` model in `models.py`
- [ ] Add these new columns:
  ```python
  # User tracking
  user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
  
  # Portfolio tracking
  portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)
  
  # Alpaca fields
  alpaca_order_id = Column(String(100), nullable=True, index=True)
  alpaca_filled_price = Column(Numeric(15, 4), nullable=True)
  alpaca_filled_qty = Column(Integer, nullable=True)
  alpaca_status = Column(String(50), nullable=True)
  alpaca_filled_at = Column(DateTime, nullable=True)
  ```
- [ ] Add relationships to Trade model:
  ```python
  # Relationships (add after columns, before class ends)
  user = relationship("User", back_populates="trades")
  portfolio = relationship("Portfolio", back_populates="trades")
  ```

#### 4.3: Add Missing Import
- [ ] At top of `models.py`, ensure this import exists:
  ```python
  from sqlalchemy import UniqueConstraint
  ```

#### 4.4: Save and Check
- [ ] Save `models.py`
- [ ] Look for red squiggles/errors in IDE

**Verification**: All models defined, relationships configured

---

### **STEP 5: Initialize Database with New Tables** (10 min)

#### 5.1: Test Database Creation Locally
- [ ] Delete old database: `rm oms-api/trades.db` (if it exists)
- [ ] Start API: `cd oms-api && source venv/bin/activate && uvicorn app.main:app --reload`
- [ ] Check logs for "Database initialized successfully"
- [ ] No errors about tables/relationships

#### 5.2: Verify Tables Created
- [ ] Install sqlite viewer: `pip install sqlite-web` (optional)
- [ ] Or use any SQLite browser
- [ ] Open `oms-api/trades.db`
- [ ] Verify tables exist:
  - users
  - roles
  - portfolios
  - portfolio_access
  - trades (with new columns)

#### 5.3: Stop Server
- [ ] Press Ctrl+C to stop

**Verification**: Database has all 5 tables with correct schema

---

### **STEP 6: Seed Database with Default Roles** (10 min)

#### 6.1: Create Seed Data Script
- [ ] Create file: `oms-api/seed_data.py`
- [ ] Add content:
  ```python
  """Seed database with default roles and admin user"""
  from app.database import SessionLocal, init_db
  from app.models import Role, User
  from app.config import settings
  import logging
  
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)
  
  def seed_roles():
      """Create default roles"""
      db = SessionLocal()
      
      try:
          # Check if roles already exist
          existing = db.query(Role).first()
          if existing:
              logger.info("Roles already seeded")
              return
          
          roles = [
              Role(
                  name="admin",
                  description="Full system access",
                  can_create_trade=True,
                  can_view_all_trades=True,
                  can_manage_portfolios=True,
                  max_trade_value=None
              ),
              Role(
                  name="trader",
                  description="Can execute trades",
                  can_create_trade=True,
                  can_view_all_trades=False,
                  can_manage_portfolios=False,
                  max_trade_value=50000.00
              ),
              Role(
                  name="analyst",
                  description="Read-only access for analysis",
                  can_create_trade=False,
                  can_view_all_trades=True,
                  can_manage_portfolios=False,
                  max_trade_value=0
              ),
              Role(
                  name="viewer",
                  description="Limited view access",
                  can_create_trade=False,
                  can_view_all_trades=False,
                  can_manage_portfolios=False,
                  max_trade_value=0
              )
          ]
          
          db.add_all(roles)
          db.commit()
          logger.info("✅ Created 4 default roles")
          
      except Exception as e:
          logger.error(f"Error seeding roles: {e}")
          db.rollback()
      finally:
          db.close()
  
  if __name__ == "__main__":
      logger.info("Initializing database...")
      init_db()
      logger.info("Seeding roles...")
      seed_roles()
      logger.info("✅ Database seeded successfully")
  ```

#### 6.2: Run Seed Script
- [ ] Run: `cd oms-api && python seed_data.py`
- [ ] Check output: "Created 4 default roles"

#### 6.3: Verify Roles in Database
- [ ] Open database viewer
- [ ] Check `roles` table has 4 records

**Verification**: 4 roles exist in database

---

### **STEP 7: Create Alpaca Client** (20 min)

#### 7.1: Create Alpaca Client File
- [ ] Create file: `oms-api/app/alpaca_client.py`
- [ ] Add complete implementation:
  ```python
  """Alpaca API client for paper trading"""
  import logging
  from typing import Optional, Dict
  from datetime import datetime
  import alpaca_trade_api as tradeapi
  from alpaca_trade_api.rest import APIError
  
  logger = logging.getLogger(__name__)
  
  class AlpacaClient:
      """Client for interacting with Alpaca Paper Trading API"""
      
      def __init__(self, api_key: str, secret_key: str, base_url: str):
          """Initialize Alpaca API client"""
          self.api = tradeapi.REST(
              api_key,
              secret_key,
              base_url,
              api_version='v2'
          )
          logger.info("Alpaca client initialized")
      
      def health_check(self) -> bool:
          """Check if Alpaca API is reachable"""
          try:
              account = self.api.get_account()
              return account.status == 'ACTIVE'
          except Exception as e:
              logger.error(f"Alpaca health check failed: {e}")
              return False
      
      def get_account(self) -> Dict:
          """Get account information"""
          try:
              account = self.api.get_account()
              return {
                  "buying_power": float(account.buying_power),
                  "cash": float(account.cash),
                  "portfolio_value": float(account.portfolio_value),
                  "status": account.status
              }
          except APIError as e:
              logger.error(f"Error getting account: {e}")
              raise
      
      def get_latest_price(self, symbol: str) -> Optional[float]:
          """Get latest price for a symbol"""
          try:
              # Get latest trade
              trade = self.api.get_latest_trade(symbol)
              return float(trade.price)
          except APIError as e:
              logger.error(f"Error getting price for {symbol}: {e}")
              return None
      
      def is_market_open(self) -> bool:
          """Check if market is currently open"""
          try:
              clock = self.api.get_clock()
              return clock.is_open
          except APIError as e:
              logger.error(f"Error checking market status: {e}")
              return False
      
      def get_market_hours(self) -> Dict:
          """Get market hours for today"""
          try:
              clock = self.api.get_clock()
              return {
                  "is_open": clock.is_open,
                  "next_open": clock.next_open.isoformat(),
                  "next_close": clock.next_close.isoformat()
              }
          except APIError as e:
              logger.error(f"Error getting market hours: {e}")
              return {"is_open": False, "next_open": None, "next_close": None}
      
      def submit_order(
          self,
          symbol: str,
          qty: int,
          side: str,
          order_type: str = "market",
          time_in_force: str = "day"
      ) -> Optional[Dict]:
          """
          Submit an order to Alpaca
          
          Args:
              symbol: Stock symbol (e.g., 'AAPL')
              qty: Quantity to trade
              side: 'buy' or 'sell'
              order_type: 'market' or 'limit'
              time_in_force: 'day', 'gtc', etc.
          
          Returns:
              Order details or None if failed
          """
          try:
              logger.info(f"Submitting order: {side} {qty} {symbol}")
              
              order = self.api.submit_order(
                  symbol=symbol.upper(),
                  qty=qty,
                  side=side.lower(),
                  type=order_type,
                  time_in_force=time_in_force
              )
              
              logger.info(f"Order submitted: {order.id}")
              
              # Wait for fill (up to 5 seconds for market orders)
              import time
              for _ in range(10):
                  order = self.api.get_order(order.id)
                  if order.status in ['filled', 'partially_filled']:
                      break
                  time.sleep(0.5)
              
              return {
                  "order_id": order.id,
                  "status": order.status,
                  "filled_qty": int(order.filled_qty) if order.filled_qty else 0,
                  "filled_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                  "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                  "symbol": order.symbol,
                  "side": order.side,
                  "qty": int(order.qty)
              }
              
          except APIError as e:
              logger.error(f"Alpaca API error: {e}")
              raise Exception(f"Failed to submit order: {str(e)}")
          except Exception as e:
              logger.error(f"Unexpected error submitting order: {e}")
              raise
      
      def get_position(self, symbol: str) -> Optional[Dict]:
          """Get current position for a symbol"""
          try:
              position = self.api.get_position(symbol)
              return {
                  "symbol": position.symbol,
                  "qty": int(position.qty),
                  "avg_entry_price": float(position.avg_entry_price),
                  "current_price": float(position.current_price),
                  "market_value": float(position.market_value),
                  "unrealized_pl": float(position.unrealized_pl)
              }
          except APIError as e:
              if "position does not exist" in str(e).lower():
                  return None
              logger.error(f"Error getting position: {e}")
              raise
  ```

#### 7.2: Test Alpaca Client Locally
- [ ] Create test file: `oms-api/test_alpaca.py`
- [ ] Add:
  ```python
  from app.config import settings
  from app.alpaca_client import AlpacaClient
  
  client = AlpacaClient(
      settings.alpaca_api_key_id,
      settings.alpaca_secret_key,
      settings.alpaca_base_url
  )
  
  print("Testing Alpaca connection...")
  print(f"Health check: {client.health_check()}")
  print(f"Account: {client.get_account()}")
  print(f"Market open: {client.is_market_open()}")
  print(f"AAPL price: {client.get_latest_price('AAPL')}")
  print("✅ All tests passed!")
  ```
- [ ] Run: `cd oms-api && python test_alpaca.py`
- [ ] Verify all checks pass

**Verification**: Alpaca client connects successfully, gets account info

---

### **STEP 8: Create Permission Checker** (15 min)

#### 8.1: Create Permissions Module
- [ ] Create file: `oms-api/app/permissions.py`
- [ ] Add implementation:
  ```python
  """Permission checking for user actions"""
  from fastapi import HTTPException, status
  from sqlalchemy.orm import Session
  from app.models import User, Role, Portfolio, PortfolioAccess
  import logging
  
  logger = logging.getLogger(__name__)
  
  class PermissionChecker:
      """Check user permissions for various actions"""
      
      def __init__(self, db: Session):
          self.db = db
      
      def get_user_by_slack_id(self, slack_user_id: str) -> User:
          """Get user by Slack ID, raise 403 if not found or inactive"""
          user = self.db.query(User).filter(
              User.slack_user_id == slack_user_id,
              User.is_active == True
          ).first()
          
          if not user:
              logger.warning(f"User not found or inactive: {slack_user_id}")
              raise HTTPException(
                  status_code=status.HTTP_403_FORBIDDEN,
                  detail="User not found or inactive. Contact admin."
              )
          
          return user
      
      def get_role(self, role_name: str) -> Role:
          """Get role by name"""
          role = self.db.query(Role).filter(Role.name == role_name).first()
          if not role:
              raise HTTPException(
                  status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                  detail=f"Role '{role_name}' not found in system"
              )
          return role
      
      def can_create_trade(self, user: User) -> bool:
          """Check if user can create trades"""
          role = self.get_role(user.role)
          
          if not role.can_create_trade:
              raise HTTPException(
                  status_code=status.HTTP_403_FORBIDDEN,
                  detail=f"Your role '{user.role}' cannot execute trades"
              )
          
          return True
      
      def can_access_portfolio(self, user: User, portfolio_id: int, required_access: str = "trade") -> bool:
          """
          Check if user can access portfolio
          
          Args:
              user: User object
              portfolio_id: Portfolio ID
              required_access: 'view', 'trade', or 'admin'
          
          Returns:
              True if access granted
          
          Raises:
              HTTPException if access denied
          """
          # Admins can access everything
          if user.role == "admin":
              return True
          
          # Check portfolio access table
          access = self.db.query(PortfolioAccess).filter(
              PortfolioAccess.portfolio_id == portfolio_id,
              PortfolioAccess.user_id == user.id
          ).first()
          
          if not access:
              raise HTTPException(
                  status_code=status.HTTP_403_FORBIDDEN,
                  detail="You don't have access to this portfolio"
              )
          
          # Check access level
          access_levels = {'view': 1, 'trade': 2, 'admin': 3}
          user_level = access_levels.get(access.access_level, 0)
          required_level = access_levels.get(required_access, 999)
          
          if user_level < required_level:
              raise HTTPException(
                  status_code=status.HTTP_403_FORBIDDEN,
                  detail=f"You have '{access.access_level}' access but need '{required_access}' access"
              )
          
          return True
      
      def validate_trade_value(self, user: User, trade_value: float) -> bool:
          """Check if trade value is within user's limits"""
          role = self.get_role(user.role)
          
          if role.max_trade_value is not None and trade_value > float(role.max_trade_value):
              raise HTTPException(
                  status_code=status.HTTP_403_FORBIDDEN,
                  detail=f"Trade value ${trade_value:,.2f} exceeds your limit of ${float(role.max_trade_value):,.2f}"
              )
          
          return True
      
      def get_user_portfolios(self, user: User, min_access: str = "view"):
          """Get all portfolios user has access to"""
          if user.role == "admin":
              # Admins see all portfolios
              return self.db.query(Portfolio).all()
          
          # Get portfolios from access table
          access_list = self.db.query(PortfolioAccess).filter(
              PortfolioAccess.user_id == user.id
          ).all()
          
          portfolio_ids = [a.portfolio_id for a in access_list]
          return self.db.query(Portfolio).filter(Portfolio.id.in_(portfolio_ids)).all()
  ```

**Verification**: File saved, no syntax errors

---

### **STEP 9: Update Trade Schemas** (10 min)

#### 9.1: Update Schemas File
- [ ] Open `oms-api/app/schemas.py`
- [ ] Add new response models at the end:
  ```python
  # Alpaca-specific responses
  class AlpacaOrderInfo(BaseModel):
      order_id: Optional[str] = None
      filled_price: Optional[float] = None
      filled_qty: Optional[int] = None
      status: Optional[str] = None
      filled_at: Optional[str] = None
  
  # User info in responses
  class UserInfo(BaseModel):
      slack_user_id: str
      name: str
      role: str
  
  # Portfolio info
  class PortfolioInfo(BaseModel):
      id: int
      name: str
      type: str
      description: Optional[str] = None
  ```

#### 9.2: Update TradeResponse
- [ ] Find `TradeResponse` class
- [ ] Add new fields:
  ```python
  # Add these fields to TradeResponse
  alpaca_order_id: Optional[str] = None
  alpaca_filled_price: Optional[float] = None
  alpaca_filled_qty: Optional[int] = None
  alpaca_status: Optional[str] = None
  user_id: Optional[int] = None
  portfolio_id: Optional[int] = None
  ```

#### 9.3: Update TradeCreate
- [ ] Find `TradeCreate` class
- [ ] Make `gmv` optional (Alpaca will calculate):
  ```python
  gmv: Optional[float] = None
  ```
- [ ] Add portfolio_id (replace portfolio_name eventually):
  ```python
  portfolio_id: Optional[int] = None
  ```

**Verification**: Schemas updated, no syntax errors

---

### **STEP 10: Update Routes with Alpaca + Permissions** (30 min)

#### 10.1: Update Trade Execution Endpoint
- [ ] Open `oms-api/app/routes.py`
- [ ] Add imports at top:
  ```python
  from app.alpaca_client import AlpacaClient
  from app.permissions import PermissionChecker
  from app.models import User, Portfolio, PortfolioAccess
  ```

#### 10.2: Modify execute_trade Function
- [ ] Find the `/trade` endpoint
- [ ] Replace entire function with:
  ```python
  @api_router.post("/trade", response_model=TradeExecutionResponse, status_code=201)
  async def execute_trade(
      trade: TradeCreate,
      db: Session = Depends(get_db),
      api_key: str = Depends(verify_api_key)
  ):
      """Execute a paper trade with Alpaca integration and permission checks"""
      from app.config import settings
      
      logger.info(f"Trade request received: {trade.symbol} {trade.quantity} {trade.side}")
      
      # Step 1: Get and validate user
      permissions = PermissionChecker(db)
      user = permissions.get_user_by_slack_id(trade.user_id)
      logger.info(f"User: {user.name} (role: {user.role})")
      
      # Step 2: Check if user can trade
      permissions.can_create_trade(user)
      
      # Step 3: Get/validate portfolio
      if trade.portfolio_id:
          portfolio = db.query(Portfolio).filter(Portfolio.id == trade.portfolio_id).first()
          if not portfolio:
              raise HTTPException(status_code=404, detail="Portfolio not found")
      elif trade.portfolio_name:
          # Legacy support - find by name
          portfolio = db.query(Portfolio).filter(Portfolio.name == trade.portfolio_name).first()
          if not portfolio:
              raise HTTPException(status_code=404, detail=f"Portfolio '{trade.portfolio_name}' not found")
      else:
          raise HTTPException(status_code=400, detail="portfolio_id or portfolio_name required")
      
      # Step 4: Check portfolio access
      permissions.can_access_portfolio(user, portfolio.id, required_access="trade")
      
      # Step 5: Alpaca integration
      alpaca_data = {}
      actual_price = None
      actual_qty = trade.quantity
      
      if settings.use_alpaca:
          try:
              logger.info("Using Alpaca for trade execution")
              alpaca = AlpacaClient(
                  settings.alpaca_api_key_id,
                  settings.alpaca_secret_key,
                  settings.alpaca_base_url
              )
              
              # Check market status
              if not alpaca.is_market_open():
                  logger.warning("Market is currently closed")
              
              # Submit order to Alpaca
              order_result = alpaca.submit_order(
                  symbol=trade.symbol,
                  qty=trade.quantity,
                  side=trade.side.value
              )
              
              alpaca_data = {
                  "alpaca_order_id": order_result["order_id"],
                  "alpaca_filled_price": order_result["filled_price"],
                  "alpaca_filled_qty": order_result["filled_qty"],
                  "alpaca_status": order_result["status"],
                  "alpaca_filled_at": datetime.fromisoformat(order_result["filled_at"]) if order_result["filled_at"] else None
              }
              
              actual_price = order_result["filled_price"]
              actual_qty = order_result["filled_qty"]
              
              logger.info(f"Alpaca order filled: {order_result['order_id']} at ${actual_price}")
              
          except Exception as e:
              logger.error(f"Alpaca error: {e}")
              raise HTTPException(status_code=503, detail=f"Alpaca API error: {str(e)}")
      else:
          logger.info("Alpaca disabled, using legacy mode")
      
      # Step 6: Calculate GMV
      if actual_price:
          gmv = actual_price * actual_qty
      elif trade.gmv:
          gmv = trade.gmv
      else:
          raise HTTPException(status_code=400, detail="GMV required when Alpaca is disabled")
      
      # Step 7: Validate trade value against user limits
      permissions.validate_trade_value(user, gmv)
      
      # Step 8: Generate trade ID
      from app.utils import generate_trade_id
      trade_id = generate_trade_id()
      
      # Step 9: Save to database
      db_trade = Trade(
          trade_id=trade_id,
          symbol=trade.symbol.upper(),
          quantity=actual_qty,
          gmv=gmv,
          side=trade.side,
          portfolio_name=portfolio.name,  # Keep for backward compatibility
          portfolio_id=portfolio.id,
          user_id=user.id,
          timestamp=datetime.utcnow(),
          **alpaca_data
      )
      
      db.add(db_trade)
      db.commit()
      db.refresh(db_trade)
      
      logger.info(f"Trade executed successfully: {trade_id} - {trade.side} {actual_qty} {trade.symbol} by {user.name}")
      
      return TradeExecutionResponse(
          trade_id=trade_id,
          status="executed",
          message=f"Trade executed successfully{'via Alpaca' if settings.use_alpaca else ''}",
          trade=TradeResponse(
              trade_id=trade_id,
              symbol=trade.symbol.upper(),
              quantity=actual_qty,
              gmv=gmv,
              side=trade.side,
              portfolio_name=portfolio.name,
              portfolio_id=portfolio.id,
              user_id=user.id,
              timestamp=db_trade.timestamp.isoformat(),
              created_at=db_trade.created_at.isoformat(),
              **alpaca_data
          )
      )
  ```

**Verification**: Function updated, check for syntax errors

---

### **STEP 11: Update Health Check** (5 min)

#### 11.1: Add Alpaca to Health Check
- [ ] Open `oms-api/app/main.py`
- [ ] Find `/health` endpoint
- [ ] Update to:
  ```python
  @app.get("/health")
  async def health_check():
      """Health check endpoint with Alpaca status"""
      from app.config import settings
      
      health_data = {
          "status": "healthy",
          "service": "SlackOMS API",
          "version": settings.version,
          "timestamp": datetime.utcnow().isoformat(),
          "alpaca_enabled": settings.use_alpaca,
          "alpaca_connected": False
      }
      
      # Check Alpaca connection if enabled
      if settings.use_alpaca:
          try:
              from app.alpaca_client import AlpacaClient
              alpaca = AlpacaClient(
                  settings.alpaca_api_key_id,
                  settings.alpaca_secret_key,
                  settings.alpaca_base_url
              )
              health_data["alpaca_connected"] = alpaca.health_check()
          except Exception as e:
              logger.error(f"Alpaca health check failed: {e}")
              health_data["alpaca_error"] = str(e)
      
      return health_data
  ```

**Verification**: Health endpoint updated

---

### **STEP 12: Local Testing - Phase 1 (Basic Alpaca)** (20 min)

#### 12.1: Start Local API
- [ ] Run: `cd oms-api && source venv/bin/activate && uvicorn app.main:app --reload --port 8001`
- [ ] Check startup logs - no errors
- [ ] Database initialized

#### 12.2: Test Health Check
- [ ] Open browser: http://localhost:8001/health
- [ ] Verify response shows:
  - `"alpaca_enabled": true`
  - `"alpaca_connected": true`

#### 12.3: Create Test User Manually
- [ ] Open Python shell: `cd oms-api && python`
- [ ] Run:
  ```python
  from app.database import SessionLocal
  from app.models import User, Portfolio, PortfolioAccess
  
  db = SessionLocal()
  
  # Create admin user (you)
  user = User(
      slack_user_id="U_TEST_ADMIN",
      name="Test Admin",
      email="admin@test.com",
      role="admin",
      is_active=True
  )
  db.add(user)
  db.commit()
  db.refresh(user)
  print(f"Created user: {user.id}")
  
  # Create test portfolio
  portfolio = Portfolio(
      name="Test Portfolio",
      type="personal",
      owner_id=user.id,
      description="Test portfolio for development"
  )
  db.add(portfolio)
  db.commit()
  db.refresh(portfolio)
  print(f"Created portfolio: {portfolio.id}")
  
  # Grant access
  access = PortfolioAccess(
      portfolio_id=portfolio.id,
      user_id=user.id,
      access_level="trade"
  )
  db.add(access)
  db.commit()
  print("✅ Test user and portfolio created")
  
  db.close()
  ```
- [ ] Exit Python: `exit()`

#### 12.4: Test Trade Execution with Alpaca
- [ ] Create test script: `oms-api/test_trade.sh`
- [ ] Add:
  ```bash
  #!/bin/bash
  curl -X POST http://localhost:8001/api/v1/trade \
    -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ" \
    -H "Content-Type: application/json" \
    -d '{
      "symbol": "AAPL",
      "quantity": 10,
      "side": "BUY",
      "portfolio_id": 1,
      "user_id": "U_TEST_ADMIN"
    }' | jq
  ```
- [ ] Run: `chmod +x oms-api/test_trade.sh && ./oms-api/test_trade.sh`
- [ ] Check response:
  - Trade executed
  - Has `alpaca_order_id`
  - Has `alpaca_filled_price`
  - Status: "filled"

#### 12.5: Check Alpaca Dashboard
- [ ] Login to Alpaca: https://app.alpaca.markets/paper/dashboard/overview
- [ ] Go to "Orders" tab
- [ ] Verify your test order appears
- [ ] Check "Positions" - should show AAPL position

#### 12.6: Test Permission Denied
- [ ] Test with non-existent user:
  ```bash
  curl -X POST http://localhost:8001/api/v1/trade \
    -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ" \
    -H "Content-Type: application/json" \
    -d '{
      "symbol": "AAPL",
      "quantity": 10,
      "side": "BUY",
      "portfolio_id": 1,
      "user_id": "U_FAKE_USER"
    }'
  ```
- [ ] Should get 403 error: "User not found"

**Verification**: 
- ✅ Alpaca integration working
- ✅ Permission checks working
- ✅ Order appears in Alpaca dashboard

---

### **STEP 13: Add Admin User Management Endpoints** (25 min)

#### 13.1: Create Admin Routes File
- [ ] Create file: `oms-api/app/admin_routes.py`
- [ ] Add complete implementation (I'll provide this - it's long)

#### 13.2: Include Admin Routes in Main App
- [ ] Open `oms-api/app/main.py`
- [ ] Add import:
  ```python
  from app.admin_routes import admin_router
  ```
- [ ] Add router:
  ```python
  app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
  ```

#### 13.3: Test Admin Endpoints
- [ ] Test list users: `curl http://localhost:8001/api/v1/admin/users -H "X-API-Key: ..."`
- [ ] Should show test user

**Verification**: Admin endpoints accessible

---

### **STEP 14: Update Slack Bot** (30 min)

#### 14.1: Update Trade Modal
- [ ] Open `slack-bot/app/blocks.py`
- [ ] Modify to fetch user's portfolios from API
- [ ] Show only portfolios user can trade in

#### 14.2: Add Admin Commands
- [ ] Open `slack-bot/app/handlers/commands.py`
- [ ] Add `/admin-user-add` command
- [ ] Add `/admin-portfolio-create` command
- [ ] Add `/admin-portfolio-grant` command

#### 14.3: Update Confirmation Message
- [ ] Update to show Alpaca order ID
- [ ] Show actual filled price
- [ ] Show user name

**Verification**: Slack bot updated with new features

---

### **STEP 15: Production Deployment** (20 min)

#### 15.1: Update Render Environment Variables
- [ ] Go to Render dashboard → slackoms-api
- [ ] Add environment variables:
  - `ALPACA_API_KEY_ID` = your key
  - `ALPACA_SECRET_KEY` = your secret
  - `ALPACA_BASE_URL` = https://paper-api.alpaca.markets
  - `USE_ALPACA` = true

#### 15.2: Commit and Push
- [ ] `git add .`
- [ ] `git commit -m "Phase 3: Alpaca integration + multi-user system"`
- [ ] `git push origin main`

#### 15.3: Monitor Deployment
- [ ] Watch Render deploy (~3 min)
- [ ] Check logs for errors
- [ ] Verify health check

#### 15.4: Seed Production Database
- [ ] In Render shell or via API call
- [ ] Run seed script to create roles

**Verification**: Production deployed successfully

---

### **STEP 16: Production Testing** (15 min)

#### 16.1: Test in Slack
- [ ] `/trade AAPL` in Slack
- [ ] Fill modal
- [ ] Submit
- [ ] Check confirmation shows Alpaca data

#### 16.2: Verify Database
- [ ] Check production database has new tables
- [ ] Verify trades have Alpaca IDs

#### 16.3: Check Alpaca Dashboard
- [ ] Verify production trades appear

**Verification**: End-to-end working in production

---

### **STEP 17: Documentation** (20 min)

#### 17.1: Update README
- [ ] Add Phase 3 completion
- [ ] Document Alpaca setup
- [ ] Document user management

#### 17.2: Create User Guide
- [ ] How to add users
- [ ] How to create portfolios
- [ ] How to grant access

#### 17.3: Update Project Summary
- [ ] Mark Phase 3 complete

**Verification**: Documentation complete

---

## 🎯 Success Criteria

- [ ] ✅ Alpaca integration working (real prices)
- [ ] ✅ User management system operational
- [ ] ✅ Role-based permissions enforced
- [ ] ✅ Portfolio access control working
- [ ] ✅ Admin commands functional
- [ ] ✅ Slack bot updated with new features
- [ ] ✅ Production deployment successful
- [ ] ✅ All tests passing
- [ ] ✅ Documentation complete

---

## ⏱️ Estimated Timeline

| Section | Duration |
|---------|----------|
| Steps 0-2 | 25 min |
| Steps 3-6 | 60 min |
| Steps 7-9 | 45 min |
| Steps 10-12 | 75 min |
| Steps 13-14 | 55 min |
| Steps 15-17 | 55 min |
| **TOTAL** | **~5 hours** |

---

## 🚀 Ready to Start?

**We have a detailed plan!** 

When ready, say: **"Let's start Step 0"** and I'll guide you through each microstep.

---

*Last Updated: October 16, 2025*  
*Status: Ready to Execute*

