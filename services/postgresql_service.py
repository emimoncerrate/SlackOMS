"""
PostgreSQL Database Service for Jain Global Slack Trading Bot

Replaces DynamoDB with PostgreSQL for Render deployment.
Provides all the same functionality with relational database benefits.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from decimal import Decimal
import json

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from sqlalchemy.sql import func
import uuid

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    """User model for PostgreSQL."""
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    slack_user_id = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False, default='EXECUTION_TRADER')
    profile = Column(JSON, default={})
    permissions = Column(JSON, default=[])
    status = Column(String, default='ACTIVE')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_users_slack_id', 'slack_user_id'),
        Index('idx_users_role', 'role'),
    )

class Trade(Base):
    """Trade model for PostgreSQL."""
    __tablename__ = 'trades'
    
    trade_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    trade_type = Column(String, nullable=False)  # BUY, SELL
    price = Column(Numeric(15, 4), nullable=False)
    status = Column(String, nullable=False, default='PENDING')
    risk_level = Column(String, nullable=False, default='MEDIUM')
    risk_analysis = Column(JSON, default={})
    alpaca_order_id = Column(String)
    executed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_trades_user_id', 'user_id'),
        Index('idx_trades_symbol', 'symbol'),
        Index('idx_trades_status', 'status'),
        Index('idx_trades_created_at', 'created_at'),
    )

class Position(Base):
    """Position model for PostgreSQL."""
    __tablename__ = 'positions'
    
    position_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    average_cost = Column(Numeric(15, 4), nullable=False, default=0)
    current_price = Column(Numeric(15, 4), nullable=False, default=0)
    unrealized_pnl = Column(Numeric(15, 4), nullable=False, default=0)
    realized_pnl = Column(Numeric(15, 4), nullable=False, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_positions_user_symbol', 'user_id', 'symbol', unique=True),
        Index('idx_positions_user_id', 'user_id'),
    )

class Channel(Base):
    """Channel configuration model for PostgreSQL."""
    __tablename__ = 'channels'
    
    channel_id = Column(String, primary_key=True)
    channel_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    permissions = Column(JSON, default={})
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PostgreSQLService:
    """PostgreSQL database service replacing DynamoDB functionality."""
    
    def __init__(self, database_url: str):
        """Initialize PostgreSQL connection."""
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self.create_tables()
        
        logger.info("PostgreSQL service initialized successfully")
    
    def create_tables(self):
        """Create all tables if they don't exist."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    # User operations
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        with self.get_session() as session:
            try:
                user = User(
                    user_id=user_data['user_id'],
                    slack_user_id=user_data['slack_user_id'],
                    role=user_data.get('role', 'EXECUTION_TRADER'),
                    profile=user_data.get('profile', {}),
                    permissions=user_data.get('permissions', []),
                    status=user_data.get('status', 'ACTIVE')
                )
                
                session.add(user)
                session.commit()
                session.refresh(user)
                
                return self._user_to_dict(user)
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating user: {e}")
                raise
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with self.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            return self._user_to_dict(user) if user else None
    
    def get_user_by_slack_id(self, slack_user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Slack ID."""
        with self.get_session() as session:
            user = session.query(User).filter(User.slack_user_id == slack_user_id).first()
            return self._user_to_dict(user) if user else None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user data."""
        with self.get_session() as session:
            try:
                user = session.query(User).filter(User.user_id == user_id).first()
                if not user:
                    raise ValueError(f"User {user_id} not found")
                
                for key, value in updates.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                
                session.commit()
                session.refresh(user)
                
                return self._user_to_dict(user)
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating user: {e}")
                raise
    
    # Trade operations
    def create_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new trade."""
        with self.get_session() as session:
            try:
                trade = Trade(
                    trade_id=trade_data['trade_id'],
                    user_id=trade_data['user_id'],
                    symbol=trade_data['symbol'],
                    quantity=trade_data['quantity'],
                    trade_type=trade_data['trade_type'],
                    price=Decimal(str(trade_data['price'])),
                    status=trade_data.get('status', 'PENDING'),
                    risk_level=trade_data.get('risk_level', 'MEDIUM'),
                    risk_analysis=trade_data.get('risk_analysis', {}),
                    alpaca_order_id=trade_data.get('alpaca_order_id'),
                    executed_at=trade_data.get('executed_at')
                )
                
                session.add(trade)
                session.commit()
                session.refresh(trade)
                
                return self._trade_to_dict(trade)
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating trade: {e}")
                raise
    
    def get_trade(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """Get trade by ID."""
        with self.get_session() as session:
            trade = session.query(Trade).filter(Trade.trade_id == trade_id).first()
            return self._trade_to_dict(trade) if trade else None
    
    def get_user_trades(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trades for a user."""
        with self.get_session() as session:
            trades = session.query(Trade)\
                .filter(Trade.user_id == user_id)\
                .order_by(Trade.created_at.desc())\
                .limit(limit)\
                .all()
            
            return [self._trade_to_dict(trade) for trade in trades]
    
    def update_trade(self, trade_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update trade data."""
        with self.get_session() as session:
            try:
                trade = session.query(Trade).filter(Trade.trade_id == trade_id).first()
                if not trade:
                    raise ValueError(f"Trade {trade_id} not found")
                
                for key, value in updates.items():
                    if hasattr(trade, key):
                        if key == 'price':
                            setattr(trade, key, Decimal(str(value)))
                        else:
                            setattr(trade, key, value)
                
                session.commit()
                session.refresh(trade)
                
                return self._trade_to_dict(trade)
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating trade: {e}")
                raise
    
    # Position operations
    def get_user_positions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all positions for a user."""
        with self.get_session() as session:
            positions = session.query(Position)\
                .filter(Position.user_id == user_id)\
                .filter(Position.quantity != 0)\
                .all()
            
            return [self._position_to_dict(position) for position in positions]
    
    def update_position(self, user_id: str, symbol: str, quantity_change: int, 
                       price: float, trade_type: str) -> Dict[str, Any]:
        """Update or create position."""
        with self.get_session() as session:
            try:
                # Get existing position
                position = session.query(Position)\
                    .filter(Position.user_id == user_id)\
                    .filter(Position.symbol == symbol)\
                    .first()
                
                if not position:
                    # Create new position
                    position = Position(
                        user_id=user_id,
                        symbol=symbol,
                        quantity=0,
                        average_cost=Decimal('0'),
                        current_price=Decimal(str(price))
                    )
                    session.add(position)
                
                # Update position based on trade type
                if trade_type.upper() == 'BUY':
                    # Calculate new average cost
                    total_cost = (position.quantity * position.average_cost) + (quantity_change * Decimal(str(price)))
                    new_quantity = position.quantity + quantity_change
                    
                    if new_quantity > 0:
                        position.average_cost = total_cost / new_quantity
                    
                    position.quantity = new_quantity
                
                elif trade_type.upper() == 'SELL':
                    # Calculate realized P&L
                    realized_pnl = quantity_change * (Decimal(str(price)) - position.average_cost)
                    position.realized_pnl += realized_pnl
                    position.quantity -= quantity_change
                
                # Update current price and unrealized P&L
                position.current_price = Decimal(str(price))
                if position.quantity > 0:
                    position.unrealized_pnl = position.quantity * (position.current_price - position.average_cost)
                else:
                    position.unrealized_pnl = Decimal('0')
                
                session.commit()
                session.refresh(position)
                
                return self._position_to_dict(position)
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating position: {e}")
                raise
    
    # Channel operations
    def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get channel configuration."""
        with self.get_session() as session:
            channel = session.query(Channel).filter(Channel.channel_id == channel_id).first()
            return self._channel_to_dict(channel) if channel else None
    
    def create_or_update_channel(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update channel configuration."""
        with self.get_session() as session:
            try:
                channel = session.query(Channel)\
                    .filter(Channel.channel_id == channel_data['channel_id'])\
                    .first()
                
                if channel:
                    # Update existing
                    for key, value in channel_data.items():
                        if hasattr(channel, key):
                            setattr(channel, key, value)
                else:
                    # Create new
                    channel = Channel(**channel_data)
                    session.add(channel)
                
                session.commit()
                session.refresh(channel)
                
                return self._channel_to_dict(channel)
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating/updating channel: {e}")
                raise
    
    # Helper methods
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert User model to dictionary."""
        return {
            'user_id': user.user_id,
            'slack_user_id': user.slack_user_id,
            'role': user.role,
            'profile': user.profile,
            'permissions': user.permissions,
            'status': user.status,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }
    
    def _trade_to_dict(self, trade: Trade) -> Dict[str, Any]:
        """Convert Trade model to dictionary."""
        return {
            'trade_id': trade.trade_id,
            'user_id': trade.user_id,
            'symbol': trade.symbol,
            'quantity': trade.quantity,
            'trade_type': trade.trade_type,
            'price': float(trade.price),
            'status': trade.status,
            'risk_level': trade.risk_level,
            'risk_analysis': trade.risk_analysis,
            'alpaca_order_id': trade.alpaca_order_id,
            'executed_at': trade.executed_at.isoformat() if trade.executed_at else None,
            'created_at': trade.created_at.isoformat() if trade.created_at else None,
            'updated_at': trade.updated_at.isoformat() if trade.updated_at else None
        }
    
    def _position_to_dict(self, position: Position) -> Dict[str, Any]:
        """Convert Position model to dictionary."""
        return {
            'position_id': position.position_id,
            'user_id': position.user_id,
            'symbol': position.symbol,
            'quantity': position.quantity,
            'average_cost': float(position.average_cost),
            'current_price': float(position.current_price),
            'unrealized_pnl': float(position.unrealized_pnl),
            'realized_pnl': float(position.realized_pnl),
            'last_updated': position.last_updated.isoformat() if position.last_updated else None,
            'created_at': position.created_at.isoformat() if position.created_at else None
        }
    
    def _channel_to_dict(self, channel: Channel) -> Dict[str, Any]:
        """Convert Channel model to dictionary."""
        return {
            'channel_id': channel.channel_id,
            'channel_name': channel.channel_name,
            'is_active': channel.is_active,
            'permissions': channel.permissions,
            'settings': channel.settings,
            'created_at': channel.created_at.isoformat() if channel.created_at else None,
            'updated_at': channel.updated_at.isoformat() if channel.updated_at else None
        }
    
    def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False