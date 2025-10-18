"""
Simple Alpaca REST API Client for Python 3.13 compatibility

Direct REST API implementation to replace alpaca-trade-api package
which has Python 3.13 compatibility issues.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class SimpleAlpacaClient:
    """Simple Alpaca REST API client using direct HTTP requests."""
    
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://paper-api.alpaca.markets"):
        """Initialize Alpaca client."""
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip('/')
        
        # Create headers for authentication
        self.headers = {
            'APCA-API-KEY-ID': api_key,
            'APCA-API-SECRET-KEY': secret_key,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"SimpleAlpacaClient initialized for {base_url}")
    
    def get_account(self) -> Optional[Dict[str, Any]]:
        """Get account information."""
        try:
            response = requests.get(
                f"{self.base_url}/v2/account",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get account: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting account: {e}")
            return None
    
    def submit_order(self, symbol: str, qty: int, side: str, 
                    order_type: str = "market", time_in_force: str = "day") -> Optional[Dict[str, Any]]:
        """Submit a paper trading order."""
        try:
            order_data = {
                "symbol": symbol.upper(),
                "qty": str(qty),
                "side": side.lower(),
                "type": order_type.lower(),
                "time_in_force": time_in_force.lower()
            }
            
            response = requests.post(
                f"{self.base_url}/v2/orders",
                headers=self.headers,
                json=order_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Failed to submit order: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            return None
    
    def get_positions(self) -> Optional[list]:
        """Get all positions."""
        try:
            response = requests.get(
                f"{self.base_url}/v2/positions",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get positions: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return None
    
    def get_orders(self, status: str = "all", limit: int = 50) -> Optional[list]:
        """Get orders."""
        try:
            params = {
                "status": status,
                "limit": str(limit)
            }
            
            response = requests.get(
                f"{self.base_url}/v2/orders",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get orders: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return None
    
    def is_market_open(self) -> bool:
        """Check if market is open."""
        try:
            response = requests.get(
                f"{self.base_url}/v2/clock",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('is_open', False)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if Alpaca API is accessible."""
        try:
            account = self.get_account()
            return account is not None
        except Exception:
            return False