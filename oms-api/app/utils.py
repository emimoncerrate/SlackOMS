"""
Utility functions for OMS API
"""
import time
import random
import string
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models import Trade, TradeSide


def generate_trade_id() -> str:
    """
    Generate a unique trade ID
    Format: T{timestamp}{random}
    Example: T1697234567123
    """
    timestamp = int(time.time() * 1000)  # milliseconds
    random_suffix = random.randint(100, 999)
    return f"T{timestamp}{random_suffix}"


def calculate_portfolio_summary(db: Session, portfolio_name: str) -> Dict:
    """
    Calculate portfolio summary with positions
    
    Args:
        db: Database session
        portfolio_name: Name of the portfolio
    
    Returns:
        Dictionary with portfolio summary
    """
    # Get all trades for this portfolio
    trades = db.query(Trade).filter(
        Trade.portfolio_name == portfolio_name
    ).order_by(Trade.timestamp).all()
    
    if not trades:
        return {
            "portfolio_name": portfolio_name,
            "total_trades": 0,
            "total_buys": 0,
            "total_sells": 0,
            "positions": {}
        }
    
    # Calculate positions
    positions = {}
    total_buys = 0
    total_sells = 0
    
    for trade in trades:
        symbol = trade.symbol
        
        # Initialize symbol if not exists
        if symbol not in positions:
            positions[symbol] = {
                "quantity": 0,
                "total_cost": 0,
                "avg_cost": 0,
                "trades": []
            }
        
        # Update based on side
        if trade.side == TradeSide.BUY:
            positions[symbol]["quantity"] += trade.quantity
            positions[symbol]["total_cost"] += float(trade.gmv)
            total_buys += 1
        else:  # SELL
            positions[symbol]["quantity"] -= trade.quantity
            positions[symbol]["total_cost"] -= float(trade.gmv)
            total_sells += 1
        
        # Track trade
        positions[symbol]["trades"].append({
            "trade_id": trade.trade_id,
            "side": trade.side.value,
            "quantity": trade.quantity,
            "gmv": float(trade.gmv),
            "timestamp": trade.timestamp.isoformat()
        })
    
    # Calculate average cost for each position
    for symbol, pos in positions.items():
        if pos["quantity"] > 0:
            pos["avg_cost"] = round(pos["total_cost"] / pos["quantity"], 2)
        else:
            pos["avg_cost"] = 0
        
        # Clean up - remove total_cost from output
        del pos["total_cost"]
    
    return {
        "portfolio_name": portfolio_name,
        "total_trades": len(trades),
        "total_buys": total_buys,
        "total_sells": total_sells,
        "positions": positions
    }


def validate_trade_data(symbol: str, quantity: int, gmv: float, side: str) -> tuple[bool, str]:
    """
    Additional business logic validation for trade data
    
    Returns:
        (is_valid, error_message)
    """
    # Symbol validation
    if not symbol or len(symbol) > 10:
        return False, "Symbol must be 1-10 characters"
    
    # Quantity validation
    if quantity <= 0:
        return False, "Quantity must be positive"
    
    if quantity > 1000000:
        return False, "Quantity exceeds maximum (1,000,000 shares)"
    
    # GMV validation
    if gmv <= 0:
        return False, "GMV must be positive"
    
    if gmv > 100000000:  # $100M
        return False, "GMV exceeds maximum ($100,000,000)"
    
    # Side validation
    if side not in ["BUY", "SELL"]:
        return False, "Side must be BUY or SELL"
    
    # Price reasonableness check
    price_per_share = gmv / quantity
    if price_per_share < 0.01:
        return False, "Price per share too low (< $0.01)"
    
    if price_per_share > 100000:
        return False, "Price per share too high (> $100,000)"
    
    return True, ""

