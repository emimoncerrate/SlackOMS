"""
Pydantic schemas for request/response validation
Ensures data integrity and provides automatic API documentation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TradeSideEnum(str, Enum):
    """Trade side enumeration for validation"""
    BUY = "BUY"
    SELL = "SELL"


class TradeCreate(BaseModel):
    """Schema for creating a new trade"""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    quantity: int = Field(..., gt=0, description="Number of shares (must be positive)")
    gmv: Decimal = Field(..., gt=0, description="Gross Monetary Value (must be positive)")
    side: TradeSideEnum = Field(..., description="Trade side: BUY or SELL")
    portfolio_name: str = Field(..., min_length=1, max_length=100, description="Portfolio name")
    user_id: str = Field(..., min_length=1, max_length=50, description="User ID from Slack")
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        """Validate and normalize stock symbol"""
        if not v:
            raise ValueError("Symbol cannot be empty")
        # Convert to uppercase and remove whitespace
        v = v.strip().upper()
        # Basic validation - only letters
        if not v.isalpha():
            raise ValueError("Symbol must contain only letters")
        return v
    
    @field_validator('portfolio_name')
    @classmethod
    def validate_portfolio_name(cls, v):
        """Validate portfolio name"""
        if not v or not v.strip():
            raise ValueError("Portfolio name cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "quantity": 100,
                "gmv": 17500.00,
                "side": "BUY",
                "portfolio_name": "Tech Portfolio",
                "user_id": "U12345ABC"
            }
        }


class TradeResponse(BaseModel):
    """Schema for trade response"""
    id: int
    trade_id: str
    symbol: str
    quantity: int
    gmv: Decimal
    side: str
    portfolio_name: str
    user_id: str
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class TradeExecutionResponse(BaseModel):
    """Schema for successful trade execution response"""
    success: bool = True
    trade_id: str
    message: str
    trade: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "trade_id": "T1697234567123",
                "message": "Trade executed successfully",
                "trade": {
                    "symbol": "AAPL",
                    "quantity": 100,
                    "gmv": 17500.00,
                    "side": "BUY",
                    "portfolio_name": "Tech Portfolio",
                    "timestamp": "2025-10-13T14:30:00Z"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Validation Error",
                "detail": "Symbol must contain only letters"
            }
        }


class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    service: str
    version: str
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "SlackOMS API",
                "version": "1.0.0",
                "timestamp": "2025-10-13T14:30:00Z"
            }
        }


class PortfolioSummary(BaseModel):
    """Schema for portfolio summary"""
    portfolio_name: str
    total_trades: int
    total_buys: int
    total_sells: int
    positions: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "portfolio_name": "Tech Portfolio",
                "total_trades": 25,
                "total_buys": 15,
                "total_sells": 10,
                "positions": {
                    "AAPL": {"quantity": 500, "avg_cost": 175.50},
                    "MSFT": {"quantity": 200, "avg_cost": 350.00}
                }
            }
        }

