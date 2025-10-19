"""
Validation service for trade inputs.

This service provides validation for:
- Stock ticker symbols
- Trade quantities
- Buying power checks
"""

import re
import logging
from typing import Dict, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating trade inputs."""
    
    def __init__(self, alpaca_service=None, market_data_service=None):
        """
        Initialize validation service.
        
        Args:
            alpaca_service: Optional AlpacaService for symbol verification
            market_data_service: Optional MarketDataService for fallback
        """
        self.alpaca_service = alpaca_service
        self.market_data_service = market_data_service
        self.logger = logging.getLogger(__name__)
    
    def validate_ticker_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Validate ticker symbol format and existence.
        
        Args:
            symbol: Stock ticker symbol to validate
            
        Returns:
            dict: {
                "valid": bool,
                "error": str or None,
                "symbol": str (normalized uppercase)
            }
        """
        # Check if empty
        if not symbol or not symbol.strip():
            return {
                "valid": False,
                "error": "Ticker symbol is required",
                "symbol": ""
            }
        
        # Normalize to uppercase and strip whitespace
        symbol = symbol.strip().upper()
        
        # Check format: 1-5 letters only
        if not re.match(r'^[A-Z]{1,5}$', symbol):
            return {
                "valid": False,
                "error": f"Invalid ticker format '{symbol}'. Use 1-5 letters only (e.g., AAPL, TSLA)",
                "symbol": symbol
            }
        
        # Check if symbol exists via Alpaca (if available)
        if self.alpaca_service and self.alpaca_service.is_available():
            try:
                # Try to get asset info from Alpaca
                asset_info = self.alpaca_service.get_asset(symbol)
                
                if not asset_info:
                    return {
                        "valid": False,
                        "error": f"Symbol '{symbol}' not found. Please verify the ticker symbol.",
                        "symbol": symbol
                    }
                
                # Check if asset is tradeable
                if not asset_info.get('tradable', False):
                    return {
                        "valid": False,
                        "error": f"Symbol '{symbol}' is not currently tradeable.",
                        "symbol": symbol
                    }
                
                self.logger.info(f"✅ Symbol validation passed: {symbol}")
                return {
                    "valid": True,
                    "error": None,
                    "symbol": symbol
                }
                
            except Exception as e:
                self.logger.warning(f"Alpaca symbol check failed for {symbol}: {e}")
                # If Alpaca fails, accept common format but log warning
                self.logger.info(f"⚠️ Symbol validation using format only: {symbol}")
                return {
                    "valid": True,  # Accept format-valid symbols even if API fails
                    "error": None,
                    "symbol": symbol,
                    "warning": "Could not verify symbol with market data"
                }
        
        # If no Alpaca service, accept valid format
        self.logger.info(f"Symbol validation (format only): {symbol}")
        return {
            "valid": True,
            "error": None,
            "symbol": symbol
        }
    
    def validate_quantity(self, quantity: Any, max_limit: int = 10000) -> Dict[str, Any]:
        """
        Validate trade quantity.
        
        Args:
            quantity: Quantity to validate (can be str or int)
            max_limit: Maximum allowed quantity per trade
            
        Returns:
            dict: {
                "valid": bool,
                "error": str or None,
                "quantity": int or None
            }
        """
        # Check if empty
        if quantity is None or str(quantity).strip() == "":
            return {
                "valid": False,
                "error": "Quantity is required",
                "quantity": None
            }
        
        # Try to convert to integer
        try:
            qty_int = int(quantity)
        except (ValueError, TypeError):
            return {
                "valid": False,
                "error": f"Quantity must be a whole number, not '{quantity}'",
                "quantity": None
            }
        
        # Check if positive
        if qty_int <= 0:
            return {
                "valid": False,
                "error": "Quantity must be greater than 0",
                "quantity": None
            }
        
        # Check if within limit
        if qty_int > max_limit:
            return {
                "valid": False,
                "error": f"Maximum quantity per trade is {max_limit:,} shares",
                "quantity": None
            }
        
        self.logger.info(f"✅ Quantity validation passed: {qty_int}")
        return {
            "valid": True,
            "error": None,
            "quantity": qty_int
        }
    
    def validate_buying_power(
        self, 
        symbol: str, 
        quantity: int, 
        current_price: float,
        available_cash: float
    ) -> Dict[str, Any]:
        """
        Validate if user has sufficient buying power.
        
        Args:
            symbol: Stock ticker symbol
            quantity: Number of shares
            current_price: Current price per share
            available_cash: Available cash in account
            
        Returns:
            dict: {
                "valid": bool,
                "error": str or None,
                "required": float,
                "available": float
            }
        """
        required_amount = quantity * current_price
        
        if required_amount > available_cash:
            return {
                "valid": False,
                "error": f"Insufficient buying power. You need ${required_amount:,.2f} but only have ${available_cash:,.2f} available",
                "required": required_amount,
                "available": available_cash
            }
        
        self.logger.info(f"✅ Buying power check passed: ${required_amount:.2f} <= ${available_cash:.2f}")
        return {
            "valid": True,
            "error": None,
            "required": required_amount,
            "available": available_cash
        }
    
    def validate_sell_order(
        self,
        symbol: str,
        quantity: int,
        user_positions: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Validate if user has sufficient shares to sell.
        
        Args:
            symbol: Stock ticker symbol
            quantity: Number of shares to sell
            user_positions: List of user's current positions
            
        Returns:
            dict: {
                "valid": bool,
                "error": str or None,
                "owned_quantity": int
            }
        """
        # If no positions provided, we can't validate
        if user_positions is None:
            self.logger.warning("No positions provided for sell validation - skipping check")
            return {
                "valid": True,  # Allow sell to proceed if we can't check
                "error": None,
                "owned_quantity": 0
            }
        
        # Find position for this symbol
        owned_quantity = 0
        for position in user_positions:
            if position.get('symbol', '').upper() == symbol.upper():
                owned_quantity = int(position.get('qty', 0))
                break
        
        # Check if user owns any shares
        if owned_quantity == 0:
            return {
                "valid": False,
                "error": f"You don't own any shares of {symbol}. Cannot sell.",
                "owned_quantity": 0
            }
        
        # Check if user has enough shares
        if quantity > owned_quantity:
            return {
                "valid": False,
                "error": f"Insufficient shares. You only have {owned_quantity:,} shares of {symbol}, cannot sell {quantity:,}",
                "owned_quantity": owned_quantity
            }
        
        self.logger.info(f"✅ Sell validation passed: Selling {quantity} of {owned_quantity} {symbol} shares")
        return {
            "valid": True,
            "error": None,
            "owned_quantity": owned_quantity
        }
    
    def validate_trade_inputs(
        self,
        symbol: str,
        quantity: Any,
        account_cash: Optional[float] = None,
        current_price: Optional[float] = None,
        max_quantity: int = 10000
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of all trade inputs.
        
        Args:
            symbol: Stock ticker symbol
            quantity: Number of shares
            account_cash: Available cash (optional, for buying power check)
            current_price: Current stock price (optional, for buying power check)
            max_quantity: Maximum allowed quantity
            
        Returns:
            dict: {
                "valid": bool,
                "errors": dict with field-specific errors,
                "data": dict with validated data
            }
        """
        errors = {}
        validated_data = {}
        
        # Validate symbol
        symbol_result = self.validate_ticker_symbol(symbol)
        if not symbol_result["valid"]:
            errors["trade_symbol_block"] = symbol_result["error"]
        else:
            validated_data["symbol"] = symbol_result["symbol"]
        
        # Validate quantity
        quantity_result = self.validate_quantity(quantity, max_quantity)
        if not quantity_result["valid"]:
            errors["qty_shares_block"] = quantity_result["error"]
        else:
            validated_data["quantity"] = quantity_result["quantity"]
        
        # Validate buying power (if data provided)
        if (account_cash is not None and 
            current_price is not None and 
            quantity_result["valid"]):
            
            buying_power_result = self.validate_buying_power(
                validated_data.get("symbol", symbol),
                quantity_result["quantity"],
                current_price,
                account_cash
            )
            
            if not buying_power_result["valid"]:
                errors["qty_shares_block"] = buying_power_result["error"]
        
        is_valid = len(errors) == 0
        
        if is_valid:
            self.logger.info(f"✅ All trade validations passed: {validated_data}")
        else:
            self.logger.warning(f"❌ Trade validation failed: {errors}")
        
        return {
            "valid": is_valid,
            "errors": errors,
            "data": validated_data
        }


# Convenience function for quick validation
def create_validation_service(alpaca_service=None, market_data_service=None) -> ValidationService:
    """
    Factory function to create a validation service.
    
    Args:
        alpaca_service: Optional AlpacaService instance
        market_data_service: Optional MarketDataService instance
        
    Returns:
        ValidationService: Configured validation service
    """
    return ValidationService(alpaca_service, market_data_service)

