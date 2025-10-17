"""
Slack Block Kit UI Components
Defines modals, messages, and interactive elements
"""
from typing import Dict, List, Optional


def create_trade_modal(symbol: str = "", trigger_id: str = "") -> Dict:
    """
    Create the trade execution modal
    
    Args:
        symbol: Pre-filled stock symbol (optional)
        trigger_id: Slack trigger ID for opening modal
    
    Returns:
        Modal view definition
    """
    return {
        "type": "modal",
        "callback_id": "trade_modal_submit",
        "title": {
            "type": "plain_text",
            "text": "Emily's Trading Bot"
        },
        "submit": {
            "type": "plain_text",
            "text": "Execute Trade"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "symbol_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "symbol_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g., AAPL, MSFT, GOOGL"
                    },
                    "initial_value": symbol.upper() if symbol else ""
                },
                "label": {
                    "type": "plain_text",
                    "text": "Stock Symbol"
                },
                "hint": {
                    "type": "plain_text",
                    "text": "Enter the ticker symbol of the stock"
                }
            },
            {
                "type": "input",
                "block_id": "quantity_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "quantity_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g., 100"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Quantity (shares)"
                },
                "hint": {
                    "type": "plain_text",
                    "text": "Number of shares to trade"
                }
            },
            {
                "type": "input",
                "block_id": "gmv_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "gmv_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g., 17500.00"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "GMV (Gross Monetary Value)"
                },
                "hint": {
                    "type": "plain_text",
                    "text": "Total dollar value of the trade"
                }
            },
            {
                "type": "input",
                "block_id": "side_block",
                "element": {
                    "type": "static_select",
                    "action_id": "side_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select trade side"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "📈 BUY"
                            },
                            "value": "BUY"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "📉 SELL"
                            },
                            "value": "SELL"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Side"
                }
            },
            {
                "type": "input",
                "block_id": "portfolio_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "portfolio_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g., Tech Portfolio"
                    },
                    "initial_value": "Default Portfolio"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Portfolio Name"
                },
                "hint": {
                    "type": "plain_text",
                    "text": "Which portfolio to execute this trade in"
                }
            }
        ]
    }


def create_success_message(trade_data: Dict) -> List[Dict]:
    """
    Create success message blocks after trade execution
    
    Args:
        trade_data: Trade data from OMS API response
    
    Returns:
        List of Slack blocks
    """
    trade_id = trade_data.get('trade_id', 'N/A')
    trade_info = trade_data.get('trade', {})
    
    symbol = trade_info.get('symbol', 'N/A')
    quantity = trade_info.get('quantity', 0)
    gmv = trade_info.get('gmv', 0)
    side = trade_info.get('side', 'N/A')
    portfolio = trade_info.get('portfolio_name', 'N/A')
    timestamp = trade_info.get('timestamp', 'N/A')
    
    # Calculate price per share
    try:
        price_per_share = float(gmv) / int(quantity)
    except:
        price_per_share = 0
    
    # Format side with emoji
    side_emoji = "📈" if side == "BUY" else "📉"
    
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "✅ Trade Executed Successfully!"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Trade ID:*\n`{trade_id}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Symbol:*\n{symbol}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Side:*\n{side_emoji} {side}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Quantity:*\n{quantity:,} shares"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*GMV:*\n${gmv:,.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Price/Share:*\n${price_per_share:.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Portfolio:*\n{portfolio}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Executed:*\n{timestamp[:19] if timestamp != 'N/A' else timestamp}"
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
                    "text": "💡 _This is a simulated trade in the paper trading system_"
                }
            ]
        }
    ]


def create_error_message(error: str) -> List[Dict]:
    """
    Create error message blocks
    
    Args:
        error: Error message to display
    
    Returns:
        List of Slack blocks
    """
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "❌ Trade Execution Failed"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Error:*\n```{error}```"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "💡 _Please check your inputs and try again. If the problem persists, contact support._"
                }
            ]
        }
    ]


def create_help_message() -> List[Dict]:
    """
    Create help message blocks
    
    Returns:
        List of Slack blocks
    """
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📚 Paper Trading Bot Help"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*How to execute a trade:*\n\n1. Type `/trade SYMBOL` (e.g., `/trade AAPL`)\n2. Fill in the trade details in the modal\n3. Click *Execute Trade*\n4. You'll receive a confirmation with your Trade ID!"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Symbol*\nStock ticker (e.g., AAPL, MSFT)"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Quantity*\nNumber of shares to trade"
                },
                {
                    "type": "mrkdwn",
                    "text": "*GMV*\nTotal dollar value of trade"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Side*\nBUY or SELL"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Portfolio*\nWhich portfolio to use"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Paper Trading*\nAll trades are simulated"
                }
            ]
        }
    ]

