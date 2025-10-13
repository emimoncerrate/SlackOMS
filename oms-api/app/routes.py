"""
API routes for OMS
Defines all endpoints for trade execution and portfolio management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.models import Trade, TradeSide
from app.schemas import (
    TradeCreate, 
    TradeExecutionResponse, 
    TradeResponse,
    PortfolioSummary,
    ErrorResponse
)
from app.utils import generate_trade_id, calculate_portfolio_summary, validate_trade_data

logger = logging.getLogger(__name__)

from app.dependencies import verify_api_key

# Create router with API key dependency
router = APIRouter(
    prefix="/api/v1", 
    tags=["trades"],
    dependencies=[Depends(verify_api_key)]  # Apply to all routes in this router
)


@router.post("/trade", response_model=TradeExecutionResponse, status_code=status.HTTP_201_CREATED)
async def execute_trade(
    trade_data: TradeCreate,
    db: Session = Depends(get_db)
):
    """
    Execute a paper trade
    
    This is the core endpoint that:
    1. Validates the trade data
    2. Generates a unique trade ID
    3. Saves the trade to the database
    4. Returns confirmation with trade ID
    
    **Security:** Requires X-API-Key header
    """
    try:
        # Additional business logic validation
        is_valid, error_msg = validate_trade_data(
            trade_data.symbol,
            trade_data.quantity,
            float(trade_data.gmv),
            trade_data.side.value
        )
        
        if not is_valid:
            logger.error(f"Trade validation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Generate unique trade ID
        trade_id = generate_trade_id()
        
        # Create trade record
        new_trade = Trade(
            trade_id=trade_id,
            symbol=trade_data.symbol,
            quantity=trade_data.quantity,
            gmv=trade_data.gmv,
            side=TradeSide(trade_data.side.value),
            portfolio_name=trade_data.portfolio_name,
            user_id=trade_data.user_id,
            timestamp=datetime.utcnow()
        )
        
        # Save to database
        db.add(new_trade)
        db.commit()
        db.refresh(new_trade)
        
        logger.info(f"Trade executed successfully: {trade_id} - {trade_data.side} {trade_data.quantity} {trade_data.symbol}")
        
        # Return success response
        return TradeExecutionResponse(
            success=True,
            trade_id=trade_id,
            message="Trade executed successfully",
            trade={
                "symbol": new_trade.symbol,
                "quantity": new_trade.quantity,
                "gmv": float(new_trade.gmv),
                "side": new_trade.side.value,
                "portfolio_name": new_trade.portfolio_name,
                "user_id": new_trade.user_id,
                "timestamp": new_trade.timestamp.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing trade: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute trade: {str(e)}"
        )


@router.get("/trades", response_model=List[TradeResponse])
async def list_trades(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    portfolio: Optional[str] = Query(None, description="Filter by portfolio name"),
    db: Session = Depends(get_db)
):
    """
    List all trades with pagination and filtering
    
    **Query Parameters:**
    - skip: Number of records to skip (for pagination)
    - limit: Maximum records to return (default 100, max 1000)
    - symbol: Filter by stock symbol (optional)
    - portfolio: Filter by portfolio name (optional)
    
    **Security:** Requires X-API-Key header
    """
    try:
        # Build query
        query = db.query(Trade)
        
        # Apply filters
        if symbol:
            query = query.filter(Trade.symbol == symbol.upper())
        
        if portfolio:
            query = query.filter(Trade.portfolio_name == portfolio)
        
        # Order by most recent first
        query = query.order_by(desc(Trade.timestamp))
        
        # Apply pagination
        trades = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(trades)} trades (skip={skip}, limit={limit})")
        
        return trades
        
    except Exception as e:
        logger.error(f"Error listing trades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trades: {str(e)}"
        )


@router.get("/trades/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific trade by trade ID
    
    **Security:** Requires X-API-Key header
    """
    try:
        trade = db.query(Trade).filter(Trade.trade_id == trade_id).first()
        
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trade {trade_id} not found"
            )
        
        logger.info(f"Retrieved trade: {trade_id}")
        
        return trade
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trade {trade_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trade: {str(e)}"
        )


@router.get("/portfolio/{portfolio_name}", response_model=PortfolioSummary)
async def get_portfolio(
    portfolio_name: str,
    db: Session = Depends(get_db)
):
    """
    Get portfolio summary with all positions
    
    Returns:
    - Total number of trades
    - Buy/Sell breakdown
    - Current positions with average cost
    - Trade history for each symbol
    
    **Security:** Requires X-API-Key header
    """
    try:
        summary = calculate_portfolio_summary(db, portfolio_name)
        
        logger.info(f"Retrieved portfolio summary: {portfolio_name}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error retrieving portfolio {portfolio_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve portfolio: {str(e)}"
        )


@router.get("/portfolios", response_model=List[str])
async def list_portfolios(db: Session = Depends(get_db)):
    """
    List all portfolio names
    
    Returns a list of unique portfolio names from all trades
    
    **Security:** Requires X-API-Key header
    """
    try:
        portfolios = db.query(Trade.portfolio_name).distinct().all()
        portfolio_names = [p[0] for p in portfolios]
        
        logger.info(f"Retrieved {len(portfolio_names)} portfolios")
        
        return portfolio_names
        
    except Exception as e:
        logger.error(f"Error listing portfolios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve portfolios: {str(e)}"
        )

