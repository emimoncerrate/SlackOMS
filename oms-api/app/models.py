"""
Database models for OMS API
Defines the Trade table structure
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class TradeSide(str, enum.Enum):
    """Enumeration for trade side (BUY or SELL)"""
    BUY = "BUY"
    SELL = "SELL"


class Trade(Base):
    """
    Trade model - represents a single paper trade execution
    
    This is the core ledger that stores all trade activity
    """
    __tablename__ = "trades"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Trade identification
    trade_id = Column(String, unique=True, index=True, nullable=False)
    
    # Trade details
    symbol = Column(String(10), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    gmv = Column(Numeric(15, 2), nullable=False)  # Gross Monetary Value
    side = Column(SQLEnum(TradeSide), nullable=False)
    
    # Portfolio and user tracking
    portfolio_name = Column(String(100), nullable=False, index=True)
    user_id = Column(String(50), nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Trade {self.trade_id}: {self.side} {self.quantity} {self.symbol} @ ${self.gmv}>"
    
    def to_dict(self):
        """Convert trade to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "gmv": float(self.gmv),
            "side": self.side.value,
            "portfolio_name": self.portfolio_name,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "created_at": self.created_at.isoformat()
        }

