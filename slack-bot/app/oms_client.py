"""
OMS API Client
Handles all communication with the OMS API
"""
import requests
import logging
from typing import Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class OMSClient:
    """Client for interacting with the OMS API"""
    
    def __init__(self):
        self.api_url = settings.oms_api_url.rstrip('/')
        self.api_key = settings.oms_api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def execute_trade(
        self,
        symbol: str,
        quantity: int,
        gmv: float,
        side: str,
        portfolio_name: str,
        user_id: str
    ) -> Dict:
        """
        Execute a paper trade via OMS API
        
        Args:
            symbol: Stock ticker symbol
            quantity: Number of shares
            gmv: Gross Monetary Value
            side: BUY or SELL
            portfolio_name: Name of portfolio
            user_id: Slack user ID
        
        Returns:
            Response from OMS API with trade details
        
        Raises:
            Exception: If trade execution fails
        """
        endpoint = f"{self.api_url}/api/v1/trade"
        
        payload = {
            "symbol": symbol.upper(),
            "quantity": int(quantity),
            "gmv": float(gmv),
            "side": side.upper(),
            "portfolio_name": portfolio_name,
            "user_id": user_id
        }
        
        logger.info(f"Executing trade: {side} {quantity} {symbol} @ ${gmv} for user {user_id}")
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Trade executed successfully: {result.get('trade_id')}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("OMS API request timed out")
            raise Exception("Trade execution timed out. Please try again.")
        
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to OMS API")
            raise Exception("Could not connect to trading system. Please contact support.")
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"OMS API HTTP error: {e.response.status_code} - {e.response.text}")
            
            if e.response.status_code == 401:
                raise Exception("Authentication failed. Please contact support.")
            elif e.response.status_code == 400:
                # Try to extract error message
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('detail', 'Invalid trade data')
                except:
                    error_msg = "Invalid trade data"
                raise Exception(f"Trade validation failed: {error_msg}")
            else:
                raise Exception(f"Trade execution failed: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Unexpected error executing trade: {str(e)}")
            raise Exception(f"An unexpected error occurred: {str(e)}")
    
    def get_portfolio(self, portfolio_name: str) -> Dict:
        """
        Get portfolio summary
        
        Args:
            portfolio_name: Name of portfolio
        
        Returns:
            Portfolio summary data
        """
        endpoint = f"{self.api_url}/api/v1/portfolio/{portfolio_name}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching portfolio: {str(e)}")
            raise Exception(f"Could not fetch portfolio: {str(e)}")
    
    def get_trades(self, limit: int = 10, symbol: Optional[str] = None) -> list:
        """
        Get list of recent trades
        
        Args:
            limit: Maximum number of trades to return
            symbol: Optional symbol filter
        
        Returns:
            List of trade records
        """
        endpoint = f"{self.api_url}/api/v1/trades"
        params = {"limit": limit}
        
        if symbol:
            params["symbol"] = symbol.upper()
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching trades: {str(e)}")
            raise Exception(f"Could not fetch trades: {str(e)}")
    
    def health_check(self) -> bool:
        """
        Check if OMS API is reachable
        
        Returns:
            True if API is healthy, False otherwise
        """
        endpoint = f"{self.api_url}/health"
        
        try:
            response = requests.get(endpoint, timeout=5)
            return response.status_code == 200
        except:
            return False


# Global OMS client instance
oms_client = OMSClient()

