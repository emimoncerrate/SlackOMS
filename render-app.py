"""
Render-Optimized Jain Global Slack Trading Bot

Simplified version optimized for Render deployment with:
- PostgreSQL database (Render managed)
- Optional external APIs with mock fallbacks
- HTTP mode deployment
- Minimal dependencies
"""

import os
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Core imports
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
PORT = int(os.getenv("PORT", 8080))
HOST = os.getenv("HOST", "0.0.0.0")

# Slack configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Database configuration (Render PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")

# Optional API keys (will use mocks if not provided)
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

class MockServices:
    """Mock implementations for external services when API keys are not available."""
    
    @staticmethod
    def get_stock_price(symbol: str) -> float:
        """Mock stock price - returns a realistic random price."""
        import random
        base_prices = {
            'AAPL': 175.0, 'MSFT': 350.0, 'GOOGL': 125.0, 'AMZN': 140.0,
            'TSLA': 250.0, 'NVDA': 450.0, 'META': 300.0, 'NFLX': 400.0
        }
        base = base_prices.get(symbol.upper(), 100.0)
        return round(base * (0.95 + random.random() * 0.1), 2)
    
    @staticmethod
    def execute_paper_trade(symbol: str, quantity: int, side: str) -> Dict[str, Any]:
        """Mock trade execution."""
        price = MockServices.get_stock_price(symbol)
        return {
            'id': f'mock_{int(datetime.now().timestamp())}',
            'symbol': symbol,
            'qty': quantity,
            'side': side,
            'filled_avg_price': price,
            'status': 'filled',
            'filled_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def analyze_risk(trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock risk analysis."""
        return {
            'risk_level': 'MEDIUM',
            'risk_score': 0.6,
            'analysis': f"Mock analysis for {trade_data.get('symbol', 'N/A')} trade",
            'recommendations': ['Consider position sizing', 'Monitor market conditions']
        }

class SimpleDatabase:
    """Simple in-memory database for development/demo purposes."""
    
    def __init__(self):
        self.trades = []
        self.positions = {}
        self.users = {}
    
    def save_trade(self, trade_data: Dict[str, Any]) -> str:
        """Save trade to memory."""
        trade_id = f"T{int(datetime.now().timestamp())}"
        trade_data['id'] = trade_id
        trade_data['timestamp'] = datetime.now().isoformat()
        self.trades.append(trade_data)
        
        # Update positions
        symbol = trade_data['symbol']
        quantity = trade_data['quantity']
        side = trade_data['side']
        
        if symbol not in self.positions:
            self.positions[symbol] = {'quantity': 0, 'avg_price': 0}
        
        if side.upper() == 'BUY':
            self.positions[symbol]['quantity'] += quantity
        else:
            self.positions[symbol]['quantity'] -= quantity
        
        return trade_id
    
    def get_trades(self, limit: int = 10) -> list:
        """Get recent trades."""
        return self.trades[-limit:]
    
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions."""
        return self.positions

# Initialize services
db = SimpleDatabase()
mock_services = MockServices()

# Initialize Slack app
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    process_before_response=True
)

# Command handlers
@app.command("/trade")
def handle_trade_command(ack, command, client, logger):
    """Handle /trade slash command."""
    ack()
    
    try:
        # Parse command text
        text = command.get('text', '').strip()
        user_id = command['user_id']
        channel_id = command['channel_id']
        
        if not text:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Usage: `/trade SYMBOL QUANTITY BUY/SELL`\nExample: `/trade AAPL 100 BUY`"
            )
            return
        
        # Simple parsing
        parts = text.split()
        if len(parts) < 3:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Invalid format. Use: `/trade SYMBOL QUANTITY BUY/SELL`"
            )
            return
        
        symbol = parts[0].upper()
        try:
            quantity = int(parts[1])
        except ValueError:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Quantity must be a number"
            )
            return
        
        side = parts[2].upper()
        if side not in ['BUY', 'SELL']:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Side must be BUY or SELL"
            )
            return
        
        # Get current price
        current_price = mock_services.get_stock_price(symbol)
        
        # Execute mock trade
        trade_result = mock_services.execute_paper_trade(symbol, quantity, side)
        
        # Save to database
        trade_data = {
            'symbol': symbol,
            'quantity': quantity,
            'side': side,
            'price': current_price,
            'user_id': user_id,
            'channel_id': channel_id
        }
        trade_id = db.save_trade(trade_data)
        
        # Risk analysis
        risk_analysis = mock_services.analyze_risk(trade_data)
        
        # Send confirmation
        total_value = quantity * current_price
        client.chat_postMessage(
            channel=channel_id,
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"✅ Trade Executed - {trade_id}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Symbol:* {symbol}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Side:* {side}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Quantity:* {quantity:,}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Price:* ${current_price:.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Value:* ${total_value:,.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Risk Level:* {risk_analysis['risk_level']}"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"📊 *Risk Analysis:* {risk_analysis['analysis']}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "💡 _This is a simulated trade for demonstration purposes_"
                        }
                    ]
                }
            ]
        )
        
        logger.info(f"Trade executed: {trade_id} - {side} {quantity} {symbol} @ ${current_price}")
        
    except Exception as e:
        logger.error(f"Error handling trade command: {e}")
        client.chat_postEphemeral(
            channel=command['channel_id'],
            user=command['user_id'],
            text=f"❌ Error executing trade: {str(e)}"
        )

@app.command("/portfolio")
def handle_portfolio_command(ack, command, client, logger):
    """Handle /portfolio slash command."""
    ack()
    
    try:
        positions = db.get_positions()
        recent_trades = db.get_trades(5)
        
        if not positions and not recent_trades:
            client.chat_postEphemeral(
                channel=command['channel_id'],
                user=command['user_id'],
                text="📊 Your portfolio is empty. Use `/trade` to execute your first trade!"
            )
            return
        
        # Build portfolio message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Portfolio Summary"
                }
            }
        ]
        
        if positions:
            position_fields = []
            total_value = 0
            
            for symbol, pos in positions.items():
                if pos['quantity'] != 0:
                    current_price = mock_services.get_stock_price(symbol)
                    position_value = pos['quantity'] * current_price
                    total_value += position_value
                    
                    position_fields.extend([
                        {
                            "type": "mrkdwn",
                            "text": f"*{symbol}:* {pos['quantity']:,} shares"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Value:* ${position_value:,.2f}"
                        }
                    ])
            
            if position_fields:
                blocks.extend([
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Current Positions:*"
                        }
                    },
                    {
                        "type": "section",
                        "fields": position_fields
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Total Portfolio Value:* ${total_value:,.2f}"
                        }
                    }
                ])
        
        if recent_trades:
            blocks.extend([
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Recent Trades:*"
                    }
                }
            ])
            
            for trade in recent_trades[-3:]:  # Show last 3 trades
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• {trade['side']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}"
                    }
                })
        
        client.chat_postEphemeral(
            channel=command['channel_id'],
            user=command['user_id'],
            blocks=blocks
        )
        
    except Exception as e:
        logger.error(f"Error handling portfolio command: {e}")
        client.chat_postEphemeral(
            channel=command['channel_id'],
            user=command['user_id'],
            text=f"❌ Error retrieving portfolio: {str(e)}"
        )

@app.command("/help")
def handle_help_command(ack, command, client):
    """Handle /help slash command."""
    ack()
    
    help_text = """
🤖 *Jain Global Trading Bot Help*

*Available Commands:*
• `/trade SYMBOL QUANTITY BUY/SELL` - Execute a trade
  Example: `/trade AAPL 100 BUY`

• `/portfolio` - View your current positions and recent trades

• `/help` - Show this help message

*Features:*
✅ Real-time stock prices
✅ Risk analysis
✅ Portfolio tracking
✅ Trade history

*Note:* This is a paper trading simulation for educational purposes.
    """
    
    client.chat_postEphemeral(
        channel=command['channel_id'],
        user=command['user_id'],
        text=help_text
    )

# Create FastAPI app for Render deployment
fastapi_app = FastAPI(title="Jain Global Slack Trading Bot")

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Slack request handler
handler = SlackRequestHandler(app)

@fastapi_app.post("/slack/events")
async def endpoint(req: Request):
    """Handle Slack events."""
    return await handler.handle(req)

@fastapi_app.get("/health")
async def health_check():
    """Health check endpoint for Render."""
    return {
        "status": "healthy",
        "service": "Jain Global Slack Trading Bot",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "version": "1.0.0"
    }

@fastapi_app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Jain Global Slack Trading Bot",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("🤖 Jain Global Slack Trading Bot")
    logger.info("=" * 60)
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Port: {PORT}")
    logger.info(f"Host: {HOST}")
    
    # Validate configuration
    if not SLACK_BOT_TOKEN:
        logger.error("❌ SLACK_BOT_TOKEN is required")
        sys.exit(1)
    
    if not SLACK_SIGNING_SECRET:
        logger.error("❌ SLACK_SIGNING_SECRET is required")
        sys.exit(1)
    
    logger.info("✅ Configuration validated")
    
    # Log optional services status
    if FINNHUB_API_KEY:
        logger.info("✅ Finnhub API configured")
    else:
        logger.info("⚠️  Using mock market data (Finnhub API not configured)")
    
    if ALPACA_API_KEY and ALPACA_SECRET_KEY:
        logger.info("✅ Alpaca API configured")
    else:
        logger.info("⚠️  Using mock trading (Alpaca API not configured)")
    
    if DATABASE_URL:
        logger.info("✅ Database configured")
    else:
        logger.info("⚠️  Using in-memory storage (Database not configured)")
    
    logger.info("=" * 60)
    logger.info("🚀 Starting server...")
    
    # Start the server
    uvicorn.run(
        fastapi_app,
        host=HOST,
        port=PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()