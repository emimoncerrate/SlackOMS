"""
Multi-Account Enhanced Trade Command

Extends the existing trade command to support multiple Alpaca accounts
with automatic user assignment and account selection capabilities.
"""

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from slack_bolt import App, Ack, BoltContext
from slack_sdk import WebClient
import urllib3

# Optimize connection pooling
urllib3.disable_warnings()
urllib3.util.connection.HAS_IPV6 = False  # Disable IPv6 if causing issues
from slack_sdk.errors import SlackApiError

from listeners.enhanced_trade_command import EnhancedTradeCommand, EnhancedMarketContext
from services.service_container import get_multi_alpaca_service, get_user_account_manager
from services.auth import AuthService

logger = logging.getLogger(__name__)

# Allowed channels where bot commands work
ALLOWED_CHANNELS = [
    "C09H1R7KKP1",  # Trading channel
]


class MultiAccountTradeCommand(EnhancedTradeCommand):
    """
    Enhanced trade command with multi-account support.
    
    Features:
    - Automatic user-to-account assignment
    - Account selection in trade modal
    - Account-specific trade execution
    - Account balance validation
    """
    
    def __init__(self, auth_service: AuthService):
        # Get market data service for parent class
        from services.service_container import get_market_data_service
        market_data_service = get_market_data_service()
        
        super().__init__(market_data_service, auth_service)
        self.multi_alpaca = None
        self.user_manager = None
        logger.info("MultiAccountTradeCommand initialized")
    
    def _get_services(self):
        """Lazy load services to avoid circular imports."""
        if not self.multi_alpaca:
            self.multi_alpaca = get_multi_alpaca_service()
        if not self.user_manager:
            self.user_manager = get_user_account_manager()
    
    def _parse_buy_sell_parameters(self, command_text: str, action: str) -> Dict[str, Any]:
        """
        Parse buy/sell command parameters from command text.
        
        Supports formats:
        - /buy 100 AAPL
        - /buy AAPL 100  
        - /sell 50 TSLA
        - /buy MSFT (quantity defaults to 1)
        - /sell GOOGL
        
        Args:
            command_text: Raw command text after /buy or /sell
            action: 'buy' or 'sell'
            
        Returns:
            Dict containing parsed parameters
        """
        params = {
            'symbol': None,
            'quantity': None,
            'action': action,
            'gmv': None
        }
        
        if not command_text:
            return params
        
        # Split and clean the command text
        parts = [part.strip() for part in command_text.split() if part.strip()]
        
        if not parts:
            # For empty commands, set default quantity
            params['quantity'] = 1
            return params
        
        # Parse quantity and symbol
        for part in parts:
            part_upper = part.upper()
            
            # Check if it's a number (quantity)
            if part.isdigit():
                params['quantity'] = int(part)
            
            # Check if it's a stock symbol (letters only, 1-5 chars)
            elif part.isalpha() and 1 <= len(part) <= 5:
                params['symbol'] = part_upper
        
        # Default quantity to 1 if not specified and we have a symbol
        if params['quantity'] is None and params['symbol'] is not None:
            params['quantity'] = 1
        # If no symbol provided, set default quantity to 1 anyway for empty commands
        elif params['quantity'] is None:
            params['quantity'] = 1
        
        logger.info(f"Parsed {action} parameters from '{command_text}': {params}")
        return params
    
    def _get_current_price_sync(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol synchronously.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price or None if unavailable
        """
        try:
            import asyncio
            
            # Get market data service
            from services.service_container import get_market_data_service
            market_service = get_market_data_service()
            
            # Run async price fetch in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                price = loop.run_until_complete(market_service.get_current_price(symbol))
                return price
            finally:
                loop.close()
                
        except Exception as e:
            logger.warning(f"Error getting current price for {symbol}: {e}")
            return None
    
    async def handle_buy_command_async(self, body: Dict[str, Any], 
                                     client: WebClient, context: BoltContext) -> None:
        """Handle /buy command with format: /buy [quantity] [symbol]"""
        try:
            logger.info("🔍 BUY COMMAND: Starting async handler")
            await self._handle_trade_command_async(body, client, context, trade_action="buy")
            logger.info("🔍 BUY COMMAND: Handler completed")
        except Exception as e:
            logger.error(f"🚨 BUY COMMAND ERROR: {e}")
    
    async def handle_sell_command_async(self, body: Dict[str, Any], 
                                      client: WebClient, context: BoltContext) -> None:
        """Handle /sell command with format: /sell [quantity] [symbol]"""
        try:
            logger.info("🔍 SELL COMMAND: Starting async handler")
            await self._handle_trade_command_async(body, client, context, trade_action="sell")
            logger.info("🔍 SELL COMMAND: Handler completed")
        except Exception as e:
            logger.error(f"🚨 SELL COMMAND ERROR: {e}")

    async def _handle_trade_command_async(self, body: Dict[str, Any], 
                                        client: WebClient, context: BoltContext, trade_action: str = None) -> None:
        """
        Handle enhanced buy/sell command with multi-account support.
        
        Args:
            body: Slack command payload
            client: Slack WebClient instance
            context: Bolt context
            trade_action: 'buy' or 'sell'
        """
        
        try:
            # Fast initialization
            self._get_services()
            
            # Quick availability check
            if not self.multi_alpaca.is_available():
                client.chat_postEphemeral(
                    channel=body.get("channel_id"),
                    user=body.get("user_id"),
                    text="❌ Multi-account trading service is currently unavailable. Please try again later."
                )
                return
            
            # Parse command parameters first (fast)
            command_text = body.get("text", "").strip()
            logger.info(f"🔍 COMMAND DEBUG: Raw text: '{command_text}', Action: {trade_action}")
            trade_params = self._parse_buy_sell_parameters(command_text, trade_action)
            logger.info(f"🔍 COMMAND DEBUG: Parsed: {trade_params}")
            
            # Get user ID (no authentication needed for modal display)
            user_id = body.get("user_id")
            
            # Quick user account lookup
            user_account = self.user_manager.get_user_account(user_id)
            
            # If no account assigned, auto-assign quickly
            if not user_account:
                available_accounts = list(self.multi_alpaca.get_available_accounts().keys())
                if available_accounts:
                    user_account = available_accounts[0]  # Quick assignment to first account
                    # Store assignment in background
                    try:
                        await self.user_manager.assign_user_to_account(
                            user_id, user_account, "system", "quick_auto_assignment"
                        )
                    except:
                        pass  # Don't fail if assignment fails
                else:
                    client.chat_postEphemeral(
                        channel=body.get("channel_id"),
                        user=body.get("user_id"),
                        text="❌ No trading accounts available. Please contact an administrator."
                    )
                    return
            
            # Create minimal context for fast modal creation
            class QuickContext:
                def __init__(self):
                    self.user = None
                    self.channel_id = body.get("channel_id")
                    self.trigger_id = body.get("trigger_id")
                    self.symbol = trade_params.get('symbol')
                    self.quantity = trade_params.get('quantity')
                    self.action = trade_params.get('action')
                    self.gmv = trade_params.get('gmv')
                    self.account_id = user_account
                    self.account_info = None  # Will be loaded in modal if needed
            
            quick_context = QuickContext()
            logger.info(f"🔍 CONTEXT DEBUG: symbol='{quick_context.symbol}', qty={quick_context.quantity}, action='{quick_context.action}'")
            
            # Create modal quickly without heavy operations
            if trade_params.get('symbol'):
                logger.info(f"🔍 MODAL DEBUG: Using symbol '{trade_params['symbol']}'")
                modal = await self._create_quick_modal_with_symbol(trade_params['symbol'], quick_context)
            else:
                logger.info(f"🔍 MODAL DEBUG: No symbol found, using basic modal")
                modal = await self._create_quick_modal(quick_context)
            
            # Open modal immediately
            client.views_open(
                trigger_id=quick_context.trigger_id,
                view=modal
            )
            
        except Exception as e:
            logger.error(f"Error handling multi-account trade command: {e}")
            try:
                client.chat_postEphemeral(
                    channel=body.get("channel_id"),
                    user=body.get("user_id"),
                    text=f"❌ Error processing trade command. Please try again."
                )
            except:
                pass  # Don't fail on error message
    
    async def _get_or_assign_user_account(self, user_id: str) -> Optional[str]:
        """
        Get existing account assignment or auto-assign user to an account.
        
        Args:
            user_id: User identifier
            
        Returns:
            Optional[str]: Account ID if successful
        """
        try:
            # Check if user already has an account assigned
            assigned_account = self.user_manager.get_user_account(user_id)
            
            if assigned_account:
                # Verify account is still active
                available_accounts = self.multi_alpaca.get_available_accounts()
                if assigned_account in available_accounts:
                    return assigned_account
                else:
                    logger.warning(f"User {user_id} assigned to inactive account {assigned_account}")
            
            # Auto-assign user to an available account
            available_accounts = list(self.multi_alpaca.get_available_accounts().keys())
            if not available_accounts:
                logger.error("No available accounts for user assignment")
                return None
            
            assigned_account = await self.user_manager.auto_assign_user(user_id, available_accounts)
            
            if assigned_account:
                logger.info(f"✅ User {user_id} auto-assigned to account {assigned_account}")
            
            return assigned_account
            
        except Exception as e:
            logger.error(f"Error getting/assigning user account: {e}")
            return None
    
    async def _create_multi_account_modal(self, context: EnhancedMarketContext) -> Dict[str, Any]:
        """
        Create enhanced trade modal with account information.
        
        Args:
            context: Market context with account info
            
        Returns:
            Dict[str, Any]: Slack modal view
        """
        # Create the enhanced modal with live market data
        modal = {
            "type": "modal",
            "callback_id": "trade_form_submission",
            "title": {
                "type": "plain_text",
                "text": f"🏦 Trade - {context.account_info.get('account_name', 'Account') if context.account_info else 'Account'}"
            },
            "submit": {
                "type": "plain_text",
                "text": "Execute Trade"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": []
        }
        
        # Add account information section
        if context.account_info:
            account_section = self._create_account_info_section(context)
            modal["blocks"].append(account_section)
            modal["blocks"].append({"type": "divider"})
        
        # Add trading form with pre-filled values
        symbol_input = {
            "type": "input",
            "block_id": "symbol_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "symbol",
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., AAPL, TSLA, MSFT"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Stock Symbol"
            }
        }
        
        # Pre-fill symbol if provided
        if context.symbol:
            symbol_input["element"]["initial_value"] = context.symbol
        
        quantity_input = {
            "type": "input",
            "block_id": "quantity_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "quantity",
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., 100"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Quantity (shares)"
            }
        }
        
        # Pre-fill quantity if provided
        if hasattr(context, 'quantity') and context.quantity:
            quantity_input["element"]["initial_value"] = str(context.quantity)
        
        # Add GMV field
        gmv_input = {
            "type": "input",
            "block_id": "gmv_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "gmv",
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., 17500.00"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "GMV (Gross Monetary Value)"
            }
        }
        
        # Pre-fill GMV if calculated
        if hasattr(context, 'gmv') and context.gmv:
            gmv_input["element"]["initial_value"] = f"{context.gmv:.2f}"
        
        action_select = {
            "type": "input",
            "block_id": "action_select",
            "element": {
                "type": "static_select",
                "action_id": "action",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select trade action"
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Buy"
                        },
                        "value": "buy"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Sell"
                        },
                        "value": "sell"
                    }
                ]
            },
            "label": {
                "type": "plain_text",
                "text": "Action"
            }
        }
        
        # Pre-fill action if provided
        if hasattr(context, 'action') and context.action:
            action_select["element"]["initial_option"] = {
                "text": {
                    "type": "plain_text",
                    "text": "Buy" if context.action == "buy" else "Sell"
                },
                "value": context.action
            }
        
        modal["blocks"].extend([
            symbol_input,
            quantity_input,
            gmv_input,
            action_select,
            {
                "type": "input",
                "block_id": "order_type_select",
                "element": {
                    "type": "static_select",
                    "action_id": "order_type",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select order type"
                    },
                    "initial_option": {
                        "text": {
                            "type": "plain_text",
                            "text": "Market Order"
                        },
                        "value": "market"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Market Order"
                            },
                            "value": "market"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Limit Order"
                            },
                            "value": "limit"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Order Type"
                }
            }
        ])
        
        return modal
    
    async def _create_multi_account_modal_with_live_data(self, symbol: str, 
                                                       context: EnhancedMarketContext) -> Dict[str, Any]:
        """
        Create enhanced trade modal with live market data and account information.
        
        Args:
            symbol: Stock symbol
            context: Market context with account info
            
        Returns:
            Dict[str, Any]: Slack modal view
        """
        # Create modal with live market data
        modal = {
            "type": "modal",
            "callback_id": "trade_form_submission",
            "title": {
                "type": "plain_text",
                "text": f"🏦 Trade {symbol} - {context.account_info.get('account_name', 'Account') if context.account_info else 'Account'}"
            },
            "submit": {
                "type": "plain_text",
                "text": "Execute Trade"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": []
        }
        
        # Add account information section first
        if context.account_info:
            account_section = self._create_account_info_section(context)
            modal["blocks"].append(account_section)
            modal["blocks"].append({"type": "divider"})
        
        # Try to get live market data
        try:
            from services.service_container import get_market_data_service
            market_service = get_market_data_service()
            
            # Get current price and market data
            current_price = await market_service.get_current_price(symbol)
            market_data = await market_service.get_market_data(symbol)
            
            if current_price and market_data:
                # Add market data section
                price_change = market_data.get('change', 0)
                price_change_pct = market_data.get('change_percent', 0)
                change_emoji = "📈" if price_change >= 0 else "📉"
                
                market_text = f"📊 *{symbol} Market Data*\n"
                market_text += f"💰 Current Price: ${current_price:.2f}\n"
                market_text += f"{change_emoji} Change: ${price_change:.2f} ({price_change_pct:.2f}%)\n"
                market_text += f"📈 High: ${market_data.get('high', 0):.2f}\n"
                market_text += f"📉 Low: ${market_data.get('low', 0):.2f}\n"
                market_text += f"📊 Volume: {market_data.get('volume', 0):,}"
                
                modal["blocks"].extend([
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": market_text
                        }
                    },
                    {"type": "divider"}
                ])
        except Exception as e:
            logger.warning(f"Could not fetch live market data for {symbol}: {e}")
            # Add basic symbol info
            modal["blocks"].extend([
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"📊 *Trading {symbol}*\n_Live market data unavailable_"
                    }
                },
                {"type": "divider"}
            ])
        
        # Add trading form with pre-filled values
        symbol_input = {
            "type": "input",
            "block_id": "symbol_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "symbol",
                "initial_value": symbol
            },
            "label": {
                "type": "plain_text",
                "text": "Stock Symbol"
            }
        }
        
        quantity_input = {
            "type": "input",
            "block_id": "quantity_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "quantity",
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., 100"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Quantity (shares)"
            }
        }
        
        # Pre-fill quantity if provided in context
        if hasattr(context, 'quantity') and context.quantity:
            quantity_input["element"]["initial_value"] = str(context.quantity)
        
        # Add GMV field with calculated value
        gmv_input = {
            "type": "input",
            "block_id": "gmv_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "gmv",
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., 17500.00"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "GMV (Gross Monetary Value)"
            }
        }
        
        # Pre-fill GMV if calculated
        if hasattr(context, 'gmv') and context.gmv:
            gmv_input["element"]["initial_value"] = f"{context.gmv:.2f}"
        elif current_price and hasattr(context, 'quantity') and context.quantity:
            # Calculate GMV on the fly
            calculated_gmv = current_price * context.quantity
            gmv_input["element"]["initial_value"] = f"{calculated_gmv:.2f}"
        
        action_select = {
            "type": "input",
            "block_id": "action_select",
            "element": {
                "type": "static_select",
                "action_id": "action",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select trade action"
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Buy"
                        },
                        "value": "buy"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Sell"
                        },
                        "value": "sell"
                    }
                ]
            },
            "label": {
                "type": "plain_text",
                "text": "Action"
            }
        }
        
        # Pre-fill action if provided in context
        if hasattr(context, 'action') and context.action:
            action_select["element"]["initial_option"] = {
                "text": {
                    "type": "plain_text",
                    "text": "Buy" if context.action == "buy" else "Sell"
                },
                "value": context.action
            }
        
        modal["blocks"].extend([
            symbol_input,
            quantity_input,
            gmv_input,
            action_select,
            {
                "type": "input",
                "block_id": "order_type_select",
                "element": {
                    "type": "static_select",
                    "action_id": "order_type",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select order type"
                    },
                    "initial_option": {
                        "text": {
                            "type": "plain_text",
                            "text": "Market Order"
                        },
                        "value": "market"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Market Order"
                            },
                            "value": "market"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Limit Order"
                            },
                            "value": "limit"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Order Type"
                }
            }
        ])
        
        return modal
    
    def _create_account_info_section(self, context: EnhancedMarketContext) -> Dict[str, Any]:
        """
        Create account information section for the modal.
        
        Args:
            context: Market context with account info
            
        Returns:
            Dict[str, Any]: Account info section block
        """
        account_info = context.account_info
        
        if not account_info:
            return {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚠️ *Account Information Unavailable*"
                }
            }
        
        # Format account information
        cash = account_info.get('cash', 0)
        buying_power = account_info.get('buying_power', 0)
        portfolio_value = account_info.get('portfolio_value', 0)
        
        account_text = f"🏦 *{account_info['account_name']}*\n"
        account_text += f"💰 Cash: ${cash:,.2f}\n"
        account_text += f"⚡ Buying Power: ${buying_power:,.2f}\n"
        account_text += f"📊 Portfolio Value: ${portfolio_value:,.2f}"
        
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": account_text
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Account Details"
                },
                "action_id": "view_account_details",
                "value": context.account_id
            }
        }
    
    async def handle_trade_submission(self, ack: Ack, body: Dict[str, Any], 
                                    client: WebClient, context: BoltContext) -> None:
        """
        Handle trade form submission with multi-account support.
        
        Args:
            ack: Slack acknowledgment function
            body: Form submission payload
            client: Slack WebClient instance
            context: Bolt context
        """
        try:
            self._get_services()
            
            # Extract form values
            values = body["view"]["state"]["values"]
            
            # Get user account (auto-assign if not assigned)
            user_id = body["user"]["id"]
            user_account = self.user_manager.get_user_account(user_id)
            
            if not user_account:
                # Auto-assign user to an available account
                available_accounts = list(self.multi_alpaca.get_available_accounts().keys())
                if available_accounts:
                    user_account = await self.user_manager.auto_assign_user(user_id, available_accounts)
                    if user_account:
                        logger.info(f"✅ Auto-assigned user {user_id} to account {user_account}")
                    else:
                        ack(response_action="errors", errors={
                            "trade_symbol_block": "Failed to assign trading account. Please contact support."
                        })
                        return
                else:
                    ack(response_action="errors", errors={
                        "trade_symbol_block": "No trading accounts available. Please contact administrator."
                    })
                    return
            
            # Parse trade parameters from new interactive modal format
            symbol = self._get_form_value(values, "trade_symbol_block", "symbol_input", "")
            quantity_str = self._get_form_value(values, "qty_shares_block", "shares_input", "1")
            action = self._get_form_value(values, "trade_side_block", "trade_side_radio")
            order_type = self._get_form_value(values, "order_type_block", "order_type_select", "market")
            limit_price = self._get_form_value(values, "limit_price_block", "limit_price_input")
            
            # STEP 2: Validate inputs using ValidationService
            from services.validation_service import ValidationService
            validation_service = ValidationService(
                alpaca_service=self.multi_alpaca.get_account_client(user_account) if hasattr(self.multi_alpaca, 'get_account_client') else None
            )
            
            # Get account info for buying power check
            account_info = self.multi_alpaca.get_account_info(user_account)
            if not account_info:
                ack(response_action="errors", errors={
                    "trade_symbol_block": "Unable to retrieve account information. Please try again."
                })
                return
            
            # Get current price for validation (only for BUY orders)
            current_price = None
            if action and action.upper() == 'BUY':
                try:
                    # Try to get current price from market data
                    from services.service_container import ServiceContainer
                    container = ServiceContainer.get_instance()
                    market_service = container.get('MarketDataService')
                    if market_service:
                        quote = market_service.get_quote(symbol)
                        if quote and 'price' in quote:
                            current_price = float(quote['price'])
                            logger.info(f"Current price for {symbol}: ${current_price}")
                except Exception as e:
                    logger.warning(f"Could not fetch current price for {symbol}: {e}")
            
            # Perform comprehensive validation
            validation_result = validation_service.validate_trade_inputs(
                symbol=symbol,
                quantity=quantity_str,
                account_cash=float(account_info.get('cash', 0)) if action and action.upper() == 'BUY' else None,
                current_price=current_price,
                max_quantity=10000
            )
            
            # If validation fails, return errors to modal
            if not validation_result["valid"]:
                logger.warning(f"Trade validation failed: {validation_result['errors']}")
                ack(response_action="errors", errors=validation_result["errors"])
                return
            
            # Extract validated data
            symbol = validation_result["data"]["symbol"]
            quantity = validation_result["data"]["quantity"]
            
            # Acknowledge with clear to close modal (validation passed)
            ack(response_action="clear")
            
            # Log trade details
            logger.info(f"🎯 Executing trade for user {user_id} on account {user_account}")
            logger.info(f"📊 Trade: {action.upper()} {quantity} {symbol} ({order_type})")
            
            # Execute trade on the user's assigned account
            trade_kwargs = {}
            if limit_price and order_type in ['limit', 'stop_limit']:
                trade_kwargs['limit_price'] = float(limit_price)
            
            trade_result = await self.multi_alpaca.execute_trade(
                account_id=user_account,
                symbol=symbol,
                qty=quantity,
                side=action,
                order_type=order_type,
                **trade_kwargs
            )
            
            if trade_result:
                await self._send_trade_success_message(client, body, trade_result, account_info)
            else:
                await self._send_error_message(client, body, "Trade execution failed")
                
        except Exception as e:
            logger.error(f"Error handling trade submission: {e}")
            await self._send_error_message(client, body, f"Error processing trade: {str(e)}")
    
    def _get_form_value(self, values: Dict[str, Any], block_id: str, 
                       action_id: str, default: Any = None) -> Any:
        """
        Extract value from form submission (supports interactive modal elements).
        
        Args:
            values: Form values dictionary
            block_id: Block identifier
            action_id: Action identifier
            default: Default value if not found
            
        Returns:
            Any: Form value or default
        """
        try:
            block = values.get(block_id, {})
            action = block.get(action_id, {})
            
            # Handle radio buttons
            if "selected_option" in action:
                return action["selected_option"]["value"]
            # Handle text inputs and number inputs
            elif "value" in action:
                return action["value"]
            # Handle static selects
            elif "selected_option" in action:
                return action["selected_option"]["value"]
            else:
                return default
        except Exception:
            return default
    
    async def _send_trade_success_message(self, client: WebClient, body: Dict[str, Any], 
                                        trade_result: Dict[str, Any], 
                                        account_info: Dict[str, Any]) -> None:
        """
        Send trade success message with account information.
        
        Args:
            client: Slack WebClient
            body: Request body
            trade_result: Trade execution result
            account_info: Account information
        """
        try:
            message = f"*Trade Executed Successfully*\n\n"
            message += f"Account: {account_info['account_name']}\n"
            message += f"{trade_result['side'].upper()} {trade_result['qty']} shares of {trade_result['symbol']}\n"
            message += f"Order ID: {trade_result['order_id']}\n"
            message += f"Submitted: {trade_result['submitted_at']}\n"
            
            if trade_result.get('filled_avg_price'):
                message += f"Filled Price: ${trade_result['filled_avg_price']:.2f}\n"
            
            # Get updated account balance
            updated_account = self.multi_alpaca.get_account_info(trade_result['account_id'])
            if updated_account:
                message += f"\nUpdated Cash: ${updated_account['cash']:,.2f}"
            
            client.chat_postMessage(
                channel=body["user"]["id"],  # Send as DM
                text=message
            )
            
        except Exception as e:
            logger.error(f"Error sending trade success message: {e}")
    
    async def _send_error_message(self, client: WebClient, body: Dict[str, Any], 
                                error_message: str) -> None:
        """
        Send error message to user.
        
        Args:
            client: Slack WebClient
            body: Request body
            error_message: Error message to send
        """
        try:
            client.chat_postMessage(
                channel=body["user"]["id"],  # Send as DM
                text=f"❌ *Trade Error*\n\n{error_message}"
            )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
    
    async def _create_quick_modal(self, context) -> Dict[str, Any]:
        """
        Create a quick modal without heavy operations to avoid timeout.
        
        Args:
            context: Quick context object
            
        Returns:
            Dict[str, Any]: Slack modal view
        """
        modal = {
            "type": "modal",
            "callback_id": "trade_form_submission",
            "title": {
                "type": "plain_text",
                "text": f"📈 {context.action.title()} - Multi-Account" if hasattr(context, 'action') and context.action else "🏦 Trade - Multi-Account"
            },
            "submit": {
                "type": "plain_text",
                "text": "Execute Trade"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": []
        }
        
        # Add quick account info (without API calls)
        modal["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🏦 *Account:* {context.account_id}\n_Account details loading..._"
            }
        })
        
        modal["blocks"].append({"type": "divider"})
        
        # Add pre-filled form
        self._add_quick_form_fields(modal, context)
        
        return modal
    
    async def _create_quick_modal_with_symbol(self, symbol: str, context) -> Dict[str, Any]:
        """
        Create a quick modal with symbol pre-filled.
        
        Args:
            symbol: Stock symbol
            context: Quick context object
            
        Returns:
            Dict[str, Any]: Slack modal view
        """
        logger.info(f"🔍 DEBUG: _create_quick_modal_with_symbol called with symbol: '{symbol}'")
        modal = {
            "type": "modal",
            "callback_id": "trade_form_submission",
            "title": {
                "type": "plain_text",
                "text": f"📈 {context.action.title()} {symbol}" if hasattr(context, 'action') and context.action else f"🏦 Trade {symbol}"
            },
            "submit": {
                "type": "plain_text",
                "text": "Execute Trade"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": []
        }
        
        # Add quick account info
        modal["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🏦 *Account:* {context.account_id}\n📊 *Symbol:* {symbol}\n_Market data loading..._"
            }
        })
        
        modal["blocks"].append({"type": "divider"})
        
        # Add pre-filled form
        logger.info(f"🔍 DEBUG: About to add form fields. symbol param: '{symbol}', context.symbol: '{context.symbol}'")
        self._add_quick_form_fields(modal, context)
        
        return modal
    
    def _add_quick_form_fields(self, modal: Dict[str, Any], context) -> None:
        """
        Add form fields to modal with pre-filled values.
        
        Args:
            modal: Modal dictionary to modify
            context: Context with pre-filled values
        """
        # Symbol input
        symbol_input = {
            "type": "input",
            "block_id": "symbol_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "symbol",
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., AAPL, TSLA, MSFT"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Stock Symbol"
            }
        }
        
        if context.symbol:
            logger.info(f"🔍 DEBUG: Setting symbol input initial_value to: '{context.symbol}'")
            symbol_input["element"]["initial_value"] = context.symbol
        else:
            logger.info(f"🔍 DEBUG: context.symbol is None or empty")
        
        # Quantity input
        quantity_input = {
            "type": "input",
            "block_id": "quantity_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "quantity",
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., 100"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Quantity (shares)"
            }
        }
        
        if context.quantity:
            quantity_input["element"]["initial_value"] = str(context.quantity)
        
        # GMV input
        gmv_input = {
            "type": "input",
            "block_id": "gmv_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "gmv",
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., 17500.00"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "GMV (Gross Monetary Value)"
            }
        }
        
        if context.gmv:
            gmv_input["element"]["initial_value"] = f"{context.gmv:.2f}"
        
        # Action select
        action_select = {
            "type": "input",
            "block_id": "action_select",
            "element": {
                "type": "static_select",
                "action_id": "action",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select trade action"
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Buy"
                        },
                        "value": "buy"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Sell"
                        },
                        "value": "sell"
                    }
                ]
            },
            "label": {
                "type": "plain_text",
                "text": "Action"
            }
        }
        
        if context.action:
            action_select["element"]["initial_option"] = {
                "text": {
                    "type": "plain_text",
                    "text": "Buy" if context.action == "buy" else "Sell"
                },
                "value": context.action
            }
        
        # Order type select
        order_type_select = {
            "type": "input",
            "block_id": "order_type_select",
            "element": {
                "type": "static_select",
                "action_id": "order_type",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select order type"
                },
                "initial_option": {
                    "text": {
                        "type": "plain_text",
                        "text": "Market Order"
                    },
                    "value": "market"
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Market Order"
                        },
                        "value": "market"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Limit Order"
                        },
                        "value": "limit"
                    }
                ]
            },
            "label": {
                "type": "plain_text",
                "text": "Order Type"
            }
        }
        
        # Add all fields to modal
        modal["blocks"].extend([
            symbol_input,
            quantity_input,
            gmv_input,
            action_select,
            order_type_select
        ])


async def _fetch_and_update_price(symbol: str, view_id: str, client: WebClient) -> None:
    """Fetch price and update buy modal in background."""
    try:
        print(f"🔄 BUY PRICE FETCH: Starting for {symbol}")
        
        # Get the current view to extract quantity
        try:
            view_info = client.views_info(view=view_id)
            current_view = view_info.get("view", {})
            values = current_view.get("state", {}).get("values", {})
            
            # Extract current quantity from modal state
            # Check both 'value' (user typed) and 'initial_value' (pre-filled)
            qty_block = values.get("qty_shares_block", {})
            shares_input = qty_block.get("shares_input", {})
            current_quantity = shares_input.get("value") or shares_input.get("initial_value", "1")
            if not current_quantity or str(current_quantity).strip() == "":
                current_quantity = "1"
            print(f"✅ BUY PRICE FETCH: Current quantity in modal: {current_quantity}")
        except Exception as e:
            print(f"⚠️ BUY PRICE FETCH: Could not extract quantity, using default: {e}")
            current_quantity = "1"
        
        # Import here to avoid circular imports
        from services.service_container import get_market_data_service
        
        market_service = get_market_data_service()
        print(f"✅ BUY PRICE FETCH: Market service obtained")
        
        # Get current price
        quote = await market_service.get_quote(symbol)
        current_price = float(quote.current_price)
        print(f"✅ BUY PRICE FETCH: Got price ${current_price:.2f} for {symbol}")
        
        # Update the modal with the new price using actual quantity
        updated_modal = _create_instant_buy_modal_with_price(symbol, current_quantity, current_price)
        
        response = client.views_update(
            view_id=view_id,
            view=updated_modal
        )
        
        if response.get("ok"):
            print(f"✅ BUY PRICE FETCH: Modal updated with ${current_price:.2f} (qty: {current_quantity})")
        else:
            print(f"❌ BUY PRICE FETCH: Modal update failed: {response}")
            
    except Exception as e:
        print(f"❌ BUY PRICE FETCH: Error: {e}")
        import traceback
        print(f"🚨 BUY PRICE FETCH: Traceback: {traceback.format_exc()}")


async def _fetch_and_update_sell_price(symbol: str, view_id: str, client: WebClient) -> None:
    """Fetch price and update sell modal in background."""
    try:
        print(f"🔄 SELL PRICE FETCH: Starting for {symbol}")
        
        # Get the current view to extract quantity
        try:
            view_info = client.views_info(view=view_id)
            current_view = view_info.get("view", {})
            values = current_view.get("state", {}).get("values", {})
            
            # Extract current quantity from modal state
            # Check both 'value' (user typed) and 'initial_value' (pre-filled)
            qty_block = values.get("qty_shares_block", {})
            shares_input = qty_block.get("shares_input", {})
            current_quantity = shares_input.get("value") or shares_input.get("initial_value", "1")
            if not current_quantity or str(current_quantity).strip() == "":
                current_quantity = "1"
            print(f"✅ SELL PRICE FETCH: Current quantity in modal: {current_quantity}")
        except Exception as e:
            print(f"⚠️ SELL PRICE FETCH: Could not extract quantity, using default: {e}")
            current_quantity = "1"
        
        # Import here to avoid circular imports
        from services.service_container import get_market_data_service
        
        market_service = get_market_data_service()
        print(f"✅ SELL PRICE FETCH: Market service obtained")
        
        # Get current price
        quote = await market_service.get_quote(symbol)
        current_price = float(quote.current_price)
        print(f"✅ SELL PRICE FETCH: Got price ${current_price:.2f} for {symbol}")
        
        # Update the modal with the new price (sell modal) using actual quantity
        updated_modal = _create_instant_sell_modal_with_price(symbol, current_quantity, current_price)
        
        response = client.views_update(
            view_id=view_id,
            view=updated_modal
        )
        
        if response.get("ok"):
            print(f"✅ SELL PRICE FETCH: Modal updated with ${current_price:.2f} (qty: {current_quantity})")
        else:
            print(f"❌ SELL PRICE FETCH: Modal update failed: {response}")
            
    except Exception as e:
        print(f"❌ SELL PRICE FETCH: Error: {e}")
        import traceback
        print(f"🚨 SELL PRICE FETCH: Traceback: {traceback.format_exc()}")


async def _fetch_and_update_buy_price(symbol: str, view_id: str, client: WebClient, quantity: str = "1") -> None:
    """Fetch price and update buy modal in background."""
    try:
        print(f"🔄 BUY PRICE FETCH: Starting for {symbol} (qty: {quantity})")
        
        # Use the passed quantity parameter
        current_quantity = quantity
        print(f"✅ BUY PRICE FETCH: Using quantity: {current_quantity}")
        
        # Import here to avoid circular imports
        from services.service_container import get_market_data_service
        
        market_service = get_market_data_service()
        print(f"✅ BUY PRICE FETCH: Market service obtained")
        
        # Validate symbol and get current price
        try:
            quote = await market_service.get_quote(symbol)
            current_price = float(quote.current_price)
            print(f"✅ BUY PRICE FETCH: Got price ${current_price:.2f} for {symbol}")
            
            # Calculate GMV with the actual quantity
            try:
                qty_num = int(current_quantity)
                calculated_gmv = qty_num * current_price
                print(f"✅ BUY PRICE FETCH: Calculated GMV: {qty_num} × ${current_price:.2f} = ${calculated_gmv:.2f}")
            except:
                calculated_gmv = current_price
                print(f"⚠️ BUY PRICE FETCH: Invalid quantity '{current_quantity}', using 1 share")
            
            # Update the modal with the new price and calculated GMV
            updated_modal = _create_instant_buy_modal_with_price_and_gmv(symbol, current_quantity, current_price, calculated_gmv)
            
            response = client.views_update(
                view_id=view_id,
                view=updated_modal
            )
            
            if response.get("ok"):
                print(f"✅ BUY PRICE FETCH: Modal updated with ${current_price:.2f} (qty: {current_quantity}, GMV: ${calculated_gmv:.2f})")
            else:
                print(f"❌ BUY PRICE FETCH: Modal update failed (Slack API error): {response}")
                # This is a modal format error, not an invalid symbol error
                
        except Exception as price_error:
            # This is actually an invalid symbol error (market data API failed)
            print(f"❌ BUY PRICE FETCH: Invalid symbol '{symbol}': {price_error}")
            
            # Create error modal for invalid symbol
            error_modal = _create_error_modal(symbol, f"Invalid ticker symbol '{symbol}'. Please try a valid stock symbol like AAPL, TSLA, MSFT.")
            
            try:
                response = client.views_update(
                    view_id=view_id,
                    view=error_modal
                )
                
                if response.get("ok"):
                    print(f"✅ BUY PRICE FETCH: Error modal displayed for invalid symbol '{symbol}'")
                else:
                    print(f"❌ BUY PRICE FETCH: Error modal update failed: {response}")
            except Exception as modal_error:
                print(f"❌ BUY PRICE FETCH: Failed to show error modal: {modal_error}")
            
    except Exception as e:
        print(f"❌ BUY PRICE FETCH: Error: {e}")
        import traceback
        print(f"🚨 BUY PRICE FETCH: Traceback: {traceback.format_exc()}")


def _create_instant_buy_modal(symbol: str = "", quantity: str = "1") -> Dict[str, Any]:
    """Create a minimal instant modal for buy command that opens immediately."""
    return {
        "type": "modal",
        "callback_id": "stock_trade_modal_interactive",
        "title": {"type": "plain_text", "text": "Emily's Trading Bot"},
        "submit": {"type": "plain_text", "text": "Execute Trade"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "trade_symbol_block",
                "label": {"type": "plain_text", "text": "Stock Symbol (e.g., AAPL)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "symbol_input",
                    "placeholder": {"type": "plain_text", "text": "Enter stock ticker (e.g., AAPL, TSLA)"},
                    "initial_value": symbol if symbol else "",
                    "dispatch_action_config": {
                        "trigger_actions_on": ["on_enter_pressed", "on_character_entered"]
                    }
                }
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Current Stock Price:* *Loading...*"},
                "block_id": "current_price_display"
            },
            {"type": "divider"},
            {
                "type": "input",
                "block_id": "trade_side_block",
                "label": {"type": "plain_text", "text": "Trade Action (Buy/Sell)"},
                "element": {
                    "type": "radio_buttons",
                    "action_id": "trade_side_radio",
                    "options": [
                        {"value": "buy", "text": {"type": "plain_text", "text": "Buy"}},
                        {"value": "sell", "text": {"type": "plain_text", "text": "Sell"}}
                    ],
                    "initial_option": {"value": "buy", "text": {"type": "plain_text", "text": "Buy"}}
                }
            },
            {
                "type": "input",
                "block_id": "qty_shares_block",
                "label": {"type": "plain_text", "text": "Quantity (shares)"},
                "element": {
                    "type": "number_input",
                    "action_id": "shares_input",
                    "placeholder": {"type": "plain_text", "text": "Enter shares, and GMV will update"},
                    "is_decimal_allowed": False,
                    "initial_value": quantity,
                    "dispatch_action_config": {
                        "trigger_actions_on": ["on_enter_pressed", "on_character_entered"]
                    }
                },
                "hint": {"type": "plain_text", "text": "Changes here trigger an automatic GMV calculation."}
            },
            {
                "type": "input",
                "block_id": "gmv_block",
                "label": {"type": "plain_text", "text": "Gross Market Value (GMV)"},
                "element": {
                    "type": "number_input",
                    "action_id": "gmv_input",
                    "placeholder": {"type": "plain_text", "text": "Enter dollar amount, and shares will update"},
                    "is_decimal_allowed": True,
                    "dispatch_action_config": {
                        "trigger_actions_on": ["on_enter_pressed", "on_character_entered"]
                    }
                },
                "hint": {"type": "plain_text", "text": "Changes here trigger an automatic Shares calculation."}
            },
            {"type": "divider"},
            {
                "type": "input",
                "block_id": "order_type_block",
                "label": {"type": "plain_text", "text": "Order Type"},
                "element": {
                    "type": "static_select",
                    "action_id": "order_type_select",
                    "initial_option": {"text": {"type": "plain_text", "text": "Market"}, "value": "market"},
                    "options": [
                        {"text": {"type": "plain_text", "text": "Market"}, "value": "market"},
                        {"text": {"type": "plain_text", "text": "Limit"}, "value": "limit"},
                        {"text": {"type": "plain_text", "text": "Stop"}, "value": "stop"},
                        {"text": {"type": "plain_text", "text": "Stop Limit"}, "value": "stop_limit"}
                    ]
                }
            }
        ]
    }


def _create_instant_buy_modal_with_price(symbol: str = "", quantity: str = "1", price: float = None) -> Dict[str, Any]:
    """Create an instant modal with actual price data."""
    modal = _create_instant_buy_modal(symbol, quantity)
    
    # Update the price display block
    if price is not None:
        for block in modal["blocks"]:
            if block.get("block_id") == "current_price_display":
                change_emoji = ""  # Default to positive
                block["text"]["text"] = f"*Current Stock Price:* ${price:.2f}"
                break
        
        # Calculate and populate initial GMV
        if quantity and quantity.isdigit():
            try:
                qty_int = int(quantity)
                calculated_gmv = qty_int * price
                
                # Find and update the GMV block
                for block in modal["blocks"]:
                    if block.get("block_id") == "gmv_block":
                        block["element"]["initial_value"] = str(calculated_gmv)
                        break
            except:
                pass
    
    return modal


def _create_instant_buy_modal_with_price_and_gmv(symbol: str = "", quantity: str = "1", price: float = None, gmv: float = None) -> Dict[str, Any]:
    """Create an instant buy modal with price and GMV pre-calculated."""
    modal = _create_instant_buy_modal(symbol, quantity)
    
    # Update the price display block
    if price is not None:
        for block in modal["blocks"]:
            if block.get("block_id") == "current_price_display":
                change_emoji = "📈"  # Default to positive for buy
                block["text"]["text"] = f"*Current Stock Price:* *${price:.2f}* {change_emoji}"
                break
    
    # Update the GMV field with calculated value
    if gmv is not None:
        for block in modal["blocks"]:
            if block.get("block_id") == "gmv_block":
                block["element"]["initial_value"] = str(round(gmv, 2))
                break
    
    return modal


def _create_error_modal(symbol: str, error_message: str) -> Dict[str, Any]:
    """Create an error modal for invalid symbols or other errors."""
    return {
        "type": "modal",
        "callback_id": "error_modal",
        "title": {"type": "plain_text", "text": "Invalid Input"},
        "close": {"type": "plain_text", "text": "Close"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"❌ *Error*\n\n{error_message}"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Valid Examples:*\n• `/buy AAPL 10` - Buy 10 shares of Apple\n• `/buy TSLA 5` - Buy 5 shares of Tesla\n• `/buy MSFT 2` - Buy 2 shares of Microsoft\n• `/sell GOOGL 3` - Sell 3 shares of Google"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Tips:*\n• Use valid stock ticker symbols (3-5 letters)\n• Quantity must be a positive number\n• Try again with a correct symbol"
                }
            }
        ]
    }


def _create_instant_sell_modal(symbol: str = "", quantity: str = "1") -> Dict[str, Any]:
    """Create a minimal instant modal for sell command that opens immediately."""
    return {
        "type": "modal",
        "callback_id": "stock_trade_modal_interactive",
        "title": {"type": "plain_text", "text": "Emily's Trading Bot"},
        "submit": {"type": "plain_text", "text": "Execute Trade"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "trade_symbol_block",
                "label": {"type": "plain_text", "text": "Stock Symbol (e.g., AAPL)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "symbol_input",
                    "placeholder": {"type": "plain_text", "text": "Enter stock ticker (e.g., AAPL, TSLA)"},
                    "initial_value": symbol if symbol else "",
                    "dispatch_action_config": {
                        "trigger_actions_on": ["on_enter_pressed", "on_character_entered"]
                    }
                }
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Current Stock Price:* *Loading...*"},
                "block_id": "current_price_display"
            },
            {"type": "divider"},
            {
                "type": "input",
                "block_id": "trade_side_block",
                "label": {"type": "plain_text", "text": "Trade Action (Buy/Sell)"},
                "element": {
                    "type": "radio_buttons",
                    "action_id": "trade_side_radio",
                    "options": [
                        {"value": "buy", "text": {"type": "plain_text", "text": "Buy"}},
                        {"value": "sell", "text": {"type": "plain_text", "text": "Sell"}}
                    ],
                    "initial_option": {"value": "sell", "text": {"type": "plain_text", "text": "Sell"}}
                }
            },
            {
                "type": "input",
                "block_id": "qty_shares_block",
                "label": {"type": "plain_text", "text": "Quantity (shares)"},
                "element": {
                    "type": "number_input",
                    "action_id": "shares_input",
                    "placeholder": {"type": "plain_text", "text": "Enter shares, and GMV will update"},
                    "is_decimal_allowed": False,
                    "initial_value": quantity,
                    "dispatch_action_config": {
                        "trigger_actions_on": ["on_enter_pressed", "on_character_entered"]
                    }
                },
                "hint": {"type": "plain_text", "text": "Changes here trigger an automatic GMV calculation."}
            },
            {
                "type": "input",
                "block_id": "gmv_block",
                "label": {"type": "plain_text", "text": "Gross Market Value (GMV)"},
                "element": {
                    "type": "number_input",
                    "action_id": "gmv_input",
                    "placeholder": {"type": "plain_text", "text": "Enter dollar amount, and shares will update"},
                    "is_decimal_allowed": True,
                    "dispatch_action_config": {
                        "trigger_actions_on": ["on_enter_pressed", "on_character_entered"]
                    }
                },
                "hint": {"type": "plain_text", "text": "Changes here trigger an automatic Shares calculation."}
            },
            {"type": "divider"},
            {
                "type": "input",
                "block_id": "order_type_block",
                "label": {"type": "plain_text", "text": "Order Type"},
                "element": {
                    "type": "static_select",
                    "action_id": "order_type_select",
                    "initial_option": {"text": {"type": "plain_text", "text": "Market"}, "value": "market"},
                    "options": [
                        {"text": {"type": "plain_text", "text": "Market"}, "value": "market"},
                        {"text": {"type": "plain_text", "text": "Limit"}, "value": "limit"},
                        {"text": {"type": "plain_text", "text": "Stop"}, "value": "stop"},
                        {"text": {"type": "plain_text", "text": "Stop Limit"}, "value": "stop_limit"}
                    ]
                }
            }
        ]
    }


def _create_instant_sell_modal_with_price(symbol: str = "", quantity: str = "1", price: float = None) -> Dict[str, Any]:
    """Create an instant sell modal with actual price data."""
    modal = _create_instant_sell_modal(symbol, quantity)
    
    # Update the price display block
    if price is not None:
        for block in modal["blocks"]:
            if block.get("block_id") == "current_price_display":
                change_emoji = ""  # Default to negative for sell
                block["text"]["text"] = f"*Current Stock Price:* ${price:.2f}"
                break
        
        # Calculate and populate initial GMV
        if quantity and quantity.isdigit():
            try:
                qty_int = int(quantity)
                calculated_gmv = qty_int * price
                
                # Find and update the GMV block
                for block in modal["blocks"]:
                    if block.get("block_id") == "gmv_block":
                        block["element"]["initial_value"] = str(calculated_gmv)
                        break
            except:
                pass
    
    return modal


async def handle_modal_interactions(ack, body, client, logger):
    """Handle interactive modal actions for real-time calculations."""
    await ack()
    
    try:
        # Get the current modal state
        view = body.get("view", {})
        values = view.get("state", {}).get("values", {})
        
        # Extract current values
        symbol_block = values.get("trade_symbol_block", {})
        symbol = symbol_block.get("symbol_input", {}).get("value", "").upper()
        
        qty_block = values.get("qty_shares_block", {})
        quantity_str = qty_block.get("shares_input", {}).get("value", "1")
        
        gmv_block = values.get("gmv_block", {})
        gmv_str = gmv_block.get("gmv_input", {}).get("value", "")
        
        order_type_block = values.get("order_type_block", {})
        order_type = order_type_block.get("order_type_select", {}).get("selected_option", {}).get("value", "market")
        
        # Get action that triggered this
        action_id = body.get("actions", [{}])[0].get("action_id", "")
        
        # Get current price if symbol is available
        current_price = None
        if symbol:
            try:
                from services.service_container import get_market_data_service
                market_service = get_market_data_service()
                quote = await market_service.get_quote(symbol)
                current_price = float(quote.current_price)
            except Exception as e:
                logger.warning(f"Failed to get price for {symbol}: {e}")
        
        # Create updated modal
        updated_blocks = []
        
        # Symbol input block
        updated_blocks.append({
            "type": "input",
            "block_id": "trade_symbol_block",
            "label": {"type": "plain_text", "text": "Stock Symbol (e.g., AAPL)"},
            "element": {
                "type": "plain_text_input",
                "action_id": "symbol_input",
                "placeholder": {"type": "plain_text", "text": "Enter the stock ticker"},
                "initial_value": symbol,
                "dispatch_action_config": {
                    "trigger_actions_on": ["on_enter_pressed", "on_character_entered"]
                }
            }
        })
        
        # Price display block
        price_text = "*Current Stock Price:* *Loading...*"
        if current_price:
            price_text = f"*Current Stock Price:* *${current_price:.2f}*"
        
        updated_blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": price_text},
            "block_id": "current_price_display"
        })
        
        updated_blocks.append({"type": "divider"})
        
        # Trade side block
        trade_side = "buy"  # Default, should be extracted from current modal
        updated_blocks.append({
            "type": "input",
            "block_id": "trade_side_block",
            "label": {"type": "plain_text", "text": "Trade Action (Buy/Sell)"},
            "element": {
                "type": "radio_buttons",
                "action_id": "trade_side_radio",
                "options": [
                    {"value": "buy", "text": {"type": "plain_text", "text": "Buy"}},
                    {"value": "sell", "text": {"type": "plain_text", "text": "Sell"}}
                ],
                "initial_option": {"value": trade_side, "text": {"type": "plain_text", "text": trade_side.title()}}
            }
        })
        
        # Calculate values based on action
        if action_id == "shares_input" and current_price and quantity_str:
            # User changed quantity, update GMV
            try:
                quantity = int(quantity_str)
                calculated_gmv = quantity * current_price
                gmv_str = f"{calculated_gmv:.2f}"
            except:
                pass
        elif action_id == "gmv_input" and current_price and gmv_str:
            # User changed GMV, update quantity
            try:
                gmv = float(gmv_str)
                calculated_quantity = int(gmv / current_price)
                quantity_str = str(calculated_quantity)
            except:
                pass
        
        # Quantity block
        updated_blocks.append({
            "type": "input",
            "block_id": "qty_shares_block",
            "label": {"type": "plain_text", "text": "Quantity (shares)"},
            "element": {
                "type": "number_input",
                "action_id": "shares_input",
                "placeholder": {"type": "plain_text", "text": "Enter shares, and GMV will update"},
                "is_decimal_allowed": False,
                "initial_value": quantity_str,
                "dispatch_action_config": {
                    "trigger_actions_on": ["on_enter_pressed", "on_character_entered"]
                }
            },
            "hint": {"type": "plain_text", "text": "Changes here trigger an automatic GMV calculation."}
        })
        
        # GMV block
        updated_blocks.append({
            "type": "input",
            "block_id": "gmv_block",
            "label": {"type": "plain_text", "text": "Gross Market Value (GMV)"},
            "element": {
                "type": "number_input",
                "action_id": "gmv_input",
                "placeholder": {"type": "plain_text", "text": "Enter dollar amount, and shares will update"},
                "is_decimal_allowed": True,
                "initial_value": gmv_str,
                "dispatch_action_config": {
                    "trigger_actions_on": ["on_enter_pressed", "on_character_entered"]
                }
            },
            "hint": {"type": "plain_text", "text": "Changes here trigger an automatic Shares calculation."}
        })
        
        updated_blocks.append({"type": "divider"})
        
        # Order type block
        updated_blocks.append({
            "type": "input",
            "block_id": "order_type_block",
            "label": {"type": "plain_text", "text": "Order Type"},
            "element": {
                "type": "static_select",
                "action_id": "order_type_select",
                "initial_option": {"text": {"type": "plain_text", "text": order_type.title()}, "value": order_type},
                "options": [
                    {"text": {"type": "plain_text", "text": "Market"}, "value": "market"},
                    {"text": {"type": "plain_text", "text": "Limit"}, "value": "limit"},
                    {"text": {"type": "plain_text", "text": "Stop"}, "value": "stop"},
                    {"text": {"type": "plain_text", "text": "Stop Limit"}, "value": "stop_limit"}
                ]
            }
        })
        
        # Limit price block (only show for limit orders)
        if order_type in ["limit", "stop_limit"]:
            updated_blocks.append({
                "type": "input",
                "block_id": "limit_price_block",
                "label": {"type": "plain_text", "text": "Limit Price (Quantity/Price for Limit Orders)"},
                "element": {
                    "type": "number_input",
                    "action_id": "limit_price_input",
                    "placeholder": {"type": "plain_text", "text": "Enter your maximum/minimum price"},
                    "is_decimal_allowed": True
                },
                "hint": {"type": "plain_text", "text": "Required for Limit or Stop Limit order types."}
            })
        
        # Update the modal
        updated_view = {
            "type": "modal",
            "callback_id": "stock_trade_modal_interactive",
            "title": {"type": "plain_text", "text": "Place Interactive Trade"},
            "submit": {"type": "plain_text", "text": "Execute Trade"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": updated_blocks
        }
        
        await client.views_update(
            view_id=view["id"],
            view=updated_view
        )
        
    except Exception as e:
        logger.error(f"Error handling modal interaction: {e}")


def register_multi_account_trade_command(app: App, auth_service: AuthService) -> MultiAccountTradeCommand:
    """
    Register multi-account trade command with the Slack app.
    
    Args:
        app: Slack Bolt app instance
        auth_service: Authentication service
        
    Returns:
        MultiAccountTradeCommand: Configured command handler
    """
    logger.info("🔧 REGISTERING MULTI-ACCOUNT BUY/SELL COMMANDS")
    multi_trade_command = MultiAccountTradeCommand(auth_service)
    
    @app.command("/buy")
    def handle_multi_account_buy_command(ack, body, client, context):
        """Handle the multi-account /buy slash command."""
        import time
        start_time = time.time()
        
        try:
            print("🔍 BUY COMMAND DEBUG: Starting buy command")
            logger.info("🔍 BUY COMMAND DEBUG: Starting buy command")
            
            # Immediate acknowledgment and terminal feedback
            ack()
            ack_time = time.time()
            print("🔍 BUY COMMAND DEBUG: ACK sent successfully")
        except Exception as e:
            print(f"❌ BUY COMMAND ACK ERROR: {e}")
            logger.error(f"❌ BUY COMMAND ACK ERROR: {e}")
            return
        
        user_id = body.get("user_id", "Unknown")
        channel_id = body.get("channel_id")
        command_text = body.get("text", "")
        trigger_id = body.get("trigger_id")
        
        # Check if command is from allowed channel
        if channel_id not in ALLOWED_CHANNELS:
            logger.warning(f"User {user_id} tried to use /buy in unauthorized channel {channel_id}")
            try:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="⚠️ This bot is only available in the designated trading channel."
                )
            except Exception as e:
                logger.error(f"Error sending channel restriction message: {e}")
            return
        
        # Immediate terminal feedback
        logger.info("=" * 60)
        logger.info("🚀 BUY COMMAND RECEIVED!")
        logger.info(f"👤 User: {user_id}")
        logger.info(f"📝 Command: /buy {command_text}")
        logger.info(f"⏰ Time: {datetime.now()}")
        logger.info(f"⚡ ACK took: {(ack_time - start_time)*1000:.2f}ms")
        logger.info("🚀 Opening modal IMMEDIATELY...")
        logger.info("=" * 60)
        
        # Parse command immediately with validation
        parse_start = time.time()
        parts = command_text.split() if command_text else []
        
        # Parse symbol: only accept valid letters, 1-5 chars
        symbol = next((p.upper() for p in parts if p.isalpha() and len(p) <= 5 and p.lower() not in ['buy', 'sell']), "")
        
        # Parse quantity: ONLY accept positive integers (reject negative, decimals, text)
        quantity_raw = next((p for p in parts if p.lstrip('-').isdigit()), "1")
        # Validate quantity is positive
        try:
            qty_int = int(quantity_raw)
            if qty_int <= 0:
                quantity = "1"  # Default to 1 if negative or zero
                logger.warning(f"Negative/zero quantity {qty_int} rejected, defaulting to 1")
            else:
                quantity = str(qty_int)
        except:
            quantity = "1"
        
        parse_time = time.time()
        logger.info(f"⚡ Parse took: {(parse_time - parse_start)*1000:.2f}ms")
        logger.info(f"Parsed values: symbol='{symbol}', quantity='{quantity}'")
        
        # Send immediate ephemeral response, then open modal
        try:
            # Removed ephemeral confirmation message - users don't need to see it
            # ephemeral_start = time.time()
            # client.chat_postEphemeral(
            #     channel=body.get("channel_id"),
            #     user=user_id,
            #     text=f"Opening buy modal for {symbol.upper() if symbol else 'stock'} (qty: {quantity})..."
            # )
            # ephemeral_time = time.time()
            # logger.info(f"⚡ Ephemeral message took: {(ephemeral_time - ephemeral_start)*1000:.2f}ms")
            
            # Create modal
            modal_start = time.time()
            modal_view = _create_instant_buy_modal(symbol, quantity)
            modal_create_time = time.time()
            logger.info(f"⚡ Modal creation took: {(modal_create_time - modal_start)*1000:.2f}ms")
            
            # Try to open modal (this might fail due to timing, but we already gave feedback)
            api_start = time.time()
            try:
                response = client.views_open(trigger_id=trigger_id, view=modal_view)
                api_time = time.time()
                logger.info(f"⚡ Slack API call took: {(api_time - api_start)*1000:.2f}ms")
                logger.info(f"⚡ TOTAL TIME: {(api_time - start_time)*1000:.2f}ms")
                
                if response.get("ok"):
                    logger.info("✅ MODAL OPENED SUCCESSFULLY!")
                    logger.info(f"📊 Symbol: {symbol}, Quantity: {quantity}")
                    
                    # If symbol is provided, fetch price in background and update modal
                    if symbol:
                        import threading
                        import asyncio
                        
                        def fetch_and_update_price():
                            try:
                                asyncio.run(_fetch_and_update_buy_price(symbol, response["view"]["id"], client, quantity))
                            except Exception as e:
                                logger.error(f"❌ Background price fetch failed: {e}")
                        
                        thread = threading.Thread(target=fetch_and_update_price)
                        thread.daemon = True
                        thread.start()
                        logger.info(f"🔄 Started background price fetch for {symbol}")
                        
                else:
                    logger.error(f"❌ Modal failed to open: {response}")
                    # Send follow-up message with manual trade option
                    client.chat_postEphemeral(
                        channel=body.get("channel_id"),
                        user=user_id,
                        text=f"⚠️ Modal timed out. Use `/buy {symbol} {quantity}` as alternative."
                    )
                    
            except Exception as modal_error:
                api_time = time.time()
                logger.error(f"❌ Modal failed after {(api_time - start_time)*1000:.2f}ms: {modal_error}")
                # Send follow-up message with manual trade option
                client.chat_postEphemeral(
                    channel=body.get("channel_id"),
                    user=user_id,
                    text=f"⚠️ Modal failed to open. Use `/buy {symbol} {quantity}` as alternative."
                )
                
        except Exception as e:
            error_time = time.time()
            logger.error(f"❌ Command failed after {(error_time - start_time)*1000:.2f}ms: {e}")
            # Simple fallback
            try:
                client.chat_postEphemeral(
                    channel=body.get("channel_id"),
                    user=user_id,
                    text=f"🚀 Buy {symbol.upper() if symbol else 'stock'} - Quantity: {quantity}\nUse `/buy {symbol} {quantity}` to execute."
                )
            except:
                pass
    


    @app.command("/sell")
    def handle_multi_account_sell_command(ack, body, client, context):
        """Handle the multi-account /sell slash command."""
        import time
        start_time = time.time()
        
        try:
            print("🔍 SELL COMMAND DEBUG: Starting sell command")
            logger.info("🔍 SELL COMMAND DEBUG: Starting sell command")
            
            # Immediate acknowledgment and terminal feedback
            ack()
            ack_time = time.time()
            print("🔍 SELL COMMAND DEBUG: ACK sent successfully")
        except Exception as e:
            print(f"❌ SELL COMMAND ACK ERROR: {e}")
            logger.error(f"❌ SELL COMMAND ACK ERROR: {e}")
            return
        
        user_id = body.get("user_id", "Unknown")
        channel_id = body.get("channel_id")
        command_text = body.get("text", "")
        trigger_id = body.get("trigger_id")
        
        # Check if command is from allowed channel
        if channel_id not in ALLOWED_CHANNELS:
            logger.warning(f"User {user_id} tried to use /sell in unauthorized channel {channel_id}")
            try:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="⚠️ This bot is only available in the designated trading channel."
                )
            except Exception as e:
                logger.error(f"Error sending channel restriction message: {e}")
            return
        
        # Immediate terminal feedback
        logger.info("=" * 60)
        logger.info("🚀 SELL COMMAND RECEIVED!")
        logger.info(f"👤 User: {user_id}")
        logger.info(f"📝 Command: /sell {command_text}")
        logger.info(f"⏰ Time: {datetime.now()}")
        logger.info(f"⚡ ACK took: {(ack_time - start_time)*1000:.2f}ms")
        logger.info("🚀 Opening modal IMMEDIATELY...")
        logger.info("=" * 60)
        
        # Parse command immediately with validation
        parse_start = time.time()
        parts = command_text.split() if command_text else []
        
        # Parse symbol: only accept valid letters, 1-5 chars
        symbol = next((p.upper() for p in parts if p.isalpha() and len(p) <= 5 and p.lower() not in ['buy', 'sell']), "")
        
        # Parse quantity: ONLY accept positive integers (reject negative, decimals, text)
        quantity_raw = next((p for p in parts if p.lstrip('-').isdigit()), "1")
        # Validate quantity is positive
        try:
            qty_int = int(quantity_raw)
            if qty_int <= 0:
                quantity = "1"  # Default to 1 if negative or zero
                logger.warning(f"Negative/zero quantity {qty_int} rejected, defaulting to 1")
            else:
                quantity = str(qty_int)
        except:
            quantity = "1"
        
        parse_time = time.time()
        logger.info(f"⚡ Parse took: {(parse_time - parse_start)*1000:.2f}ms")
        logger.info(f"Parsed values: symbol='{symbol}', quantity='{quantity}'")
        
        # Send immediate ephemeral response, then open modal
        try:
            # Removed ephemeral confirmation message - users don't need to see it
            # ephemeral_start = time.time()
            # client.chat_postEphemeral(
            #     channel=body.get("channel_id"),
            #     user=user_id,
            #     text=f"Opening sell modal for {symbol.upper() if symbol else 'stock'} (qty: {quantity})..."
            # )
            # ephemeral_time = time.time()
            # logger.info(f"⚡ Ephemeral message took: {(ephemeral_time - ephemeral_start)*1000:.2f}ms")
            
            # Create modal
            modal_start = time.time()
            modal_view = _create_instant_sell_modal(symbol, quantity)
            modal_create_time = time.time()
            logger.info(f"⚡ Modal creation took: {(modal_create_time - modal_start)*1000:.2f}ms")
            
            # Try to open modal (this might fail due to timing, but we already gave feedback)
            api_start = time.time()
            try:
                response = client.views_open(trigger_id=trigger_id, view=modal_view)
                api_time = time.time()
                logger.info(f"⚡ Slack API call took: {(api_time - api_start)*1000:.2f}ms")
                logger.info(f"⚡ TOTAL TIME: {(api_time - start_time)*1000:.2f}ms")
                
                if response.get("ok"):
                    logger.info("✅ MODAL OPENED SUCCESSFULLY!")
                    logger.info(f"📊 Symbol: {symbol}, Quantity: {quantity}")
                    
                    # If symbol is provided, fetch price in background and update modal
                    if symbol:
                        import threading
                        import asyncio
                        
                        def fetch_and_update_price():
                            try:
                                asyncio.run(_fetch_and_update_sell_price(symbol, response["view"]["id"], client))
                            except Exception as e:
                                logger.error(f"❌ Background price fetch failed: {e}")
                        
                        thread = threading.Thread(target=fetch_and_update_price)
                        thread.daemon = True
                        thread.start()
                        logger.info(f"🔄 Started background price fetch for {symbol}")
                        
                else:
                    logger.error(f"❌ Modal failed to open: {response}")
                    # Send follow-up message with manual trade option
                    client.chat_postEphemeral(
                        channel=body.get("channel_id"),
                        user=user_id,
                        text=f"⚠️ Modal timed out. Use `/sell {symbol} {quantity}` as alternative."
                    )
                    
            except Exception as modal_error:
                api_time = time.time()
                logger.error(f"❌ Modal failed after {(api_time - start_time)*1000:.2f}ms: {modal_error}")
                # Send follow-up message with manual trade option
                client.chat_postEphemeral(
                    channel=body.get("channel_id"),
                    user=user_id,
                    text=f"⚠️ Modal timed out. Use `/sell {symbol} {quantity}` as alternative."
                )
                
        except Exception as e:
            error_time = time.time()
            logger.error(f"❌ Command failed after {(error_time - start_time)*1000:.2f}ms: {e}")
            # Final fallback
            try:
                client.chat_postEphemeral(
                    channel=body.get("channel_id"),
                    user=user_id,
                    text=f"❌ Error processing command. Please try again."
                )
            except:
                pass
    

    @app.view("stock_trade_modal_interactive")
    async def handle_multi_account_trade_submission(ack, body, client, context):
        """Handle multi-account interactive trade form submission."""
        await multi_trade_command.handle_trade_submission(ack, body, client, context)
    
    # Add app mention handler for testing
    @app.event("app_mention")
    def handle_app_mention(body, say, logger):
        """Handle app mentions for testing connectivity."""
        logger.info(f"🤖 APP MENTION RECEIVED: {body}")
        text = body.get('event', {}).get('text', '')
        if 'trade' in text.lower() or 'buy' in text.lower() or 'sell' in text.lower():
            say("👋 I received your mention! Try using the `/buy` or `/sell` slash commands instead.")
        else:
            say("👋 Hello! I'm the trading bot. Use `/buy` or `/sell` to start trading!")
    
    # Register interactive action handlers for real-time calculations
    from listeners.interactive_actions import InteractiveActionHandler
    interactive_handler = InteractiveActionHandler()
    interactive_handler.register_handlers(app)
    
    # Register modal interaction handlers for GMV/Quantity calculations
    @app.action("symbol_input")
    async def handle_symbol_change(ack, body, client, logger):
        await handle_modal_interactions(ack, body, client, logger)
    
    @app.action("shares_input")
    async def handle_shares_change(ack, body, client, logger):
        await handle_modal_interactions(ack, body, client, logger)
    
    @app.action("gmv_input")
    async def handle_gmv_change(ack, body, client, logger):
        await handle_modal_interactions(ack, body, client, logger)
    
    @app.action("order_type_select")
    async def handle_order_type_change(ack, body, client, logger):
        await handle_modal_interactions(ack, body, client, logger)
    
    # Handle modal submission (when user clicks "Execute Trade")
    @app.view("stock_trade_modal_interactive")
    def handle_trade_modal_submission(ack, body, client, logger):
        """Handle trade modal submission."""
        # Acknowledge and close the modal (empty ack closes the modal)
        ack()
        
        try:
            # Extract values from modal
            values = body["view"]["state"]["values"]
            
            symbol_block = values.get("trade_symbol_block", {})
            symbol = symbol_block.get("symbol_input", {}).get("value", "").upper()
            
            qty_block = values.get("qty_shares_block", {})
            quantity = qty_block.get("shares_input", {}).get("value", "1")
            
            trade_side_block = values.get("trade_side_block", {})
            trade_side = "buy"  # Default
            if trade_side_block.get("trade_side_radio", {}).get("selected_option"):
                trade_side = trade_side_block["trade_side_radio"]["selected_option"]["value"]
            
            order_type_block = values.get("order_type_block", {})
            order_type = "market"  # Default
            if order_type_block.get("order_type_select", {}).get("selected_option"):
                order_type = order_type_block["order_type_select"]["selected_option"]["value"]
            
            limit_price = None
            if order_type in ["limit", "stop_limit"]:
                limit_price_block = values.get("limit_price_block", {})
                if limit_price_block.get("limit_price_input", {}).get("value"):
                    try:
                        limit_price = float(limit_price_block["limit_price_input"]["value"])
                    except:
                        pass
            
            user_id = body["user"]["id"]
            
            logger.info(f"🎯 TRADE SUBMISSION: {trade_side.upper()} {quantity} {symbol} ({order_type})")
            
            # Get channel from private metadata or use approved channel
            channel_id = body.get("view", {}).get("private_metadata") or "C09H1R7KKP1"  # Use first approved channel as fallback
            
            # Execute the actual trade with Alpaca in background thread
            def execute_trade_async():
                """Execute trade in background thread."""
                import asyncio
                import threading
                
                def run_trade():
                    try:
                        # Create new event loop for this thread
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Import and get services
                        from services.service_container import get_alpaca_service
                        alpaca_service = get_alpaca_service()
                        
                        # Validate inputs
                        if not symbol or not quantity:
                            raise ValueError("Missing symbol or quantity")
                        
                        qty_int = int(quantity)
                        if qty_int <= 0:
                            raise ValueError("Quantity must be positive")
                        
                        # Execute trade
                        logger.info(f"🚀 EXECUTING TRADE: {trade_side.upper()} {qty_int} {symbol}")
                        
                        if order_type == "market":
                            # Market order
                            result = loop.run_until_complete(alpaca_service.submit_order(
                                symbol=symbol,
                                quantity=qty_int,
                                side=trade_side,
                                order_type="market",
                                time_in_force="day"
                            ))
                        elif order_type == "limit" and limit_price:
                            # Limit order
                            result = loop.run_until_complete(alpaca_service.submit_order(
                                symbol=symbol,
                                quantity=qty_int,
                                side=trade_side,
                                order_type="limit",
                                time_in_force="day"
                            ))
                        else:
                            raise ValueError(f"Unsupported order type: {order_type}")
                        
                        # Send success message
                        if result and (result.get("id") or result.get("order_id")):
                            order_id = result.get("id") or result.get("order_id")
                            status = result.get("status", "submitted")
                            
                            logger.info(f"✅ TRADE EXECUTED: Order ID {order_id}, Status: {status}")
                            
                            success_msg = f"✅ **Trade Executed Successfully!**\n\n"
                            success_msg += f"📊 **Order Details:**\n"
                            success_msg += f"• Symbol: {symbol}\n"
                            success_msg += f"• Action: {trade_side.upper()}\n"
                            success_msg += f"• Quantity: {qty_int} shares\n"
                            success_msg += f"• Order Type: {order_type.title()}\n"
                            if limit_price:
                                success_msg += f"• Limit Price: ${limit_price:.2f}\n"
                            success_msg += f"• Order ID: {order_id}\n"
                            success_msg += f"• Status: {status}\n"
                            success_msg += f"\n🎯 **This is paper trading - no real money involved**"
                            
                            client.chat_postEphemeral(
                                channel=channel_id,
                                user=user_id,
                                text=success_msg
                            )
                        else:
                            logger.error(f"❌ TRADE FAILED: No order ID returned")
                            client.chat_postEphemeral(
                                channel=channel_id,
                                user=user_id,
                                text=f"❌ **Trade Failed**\n\nUnable to execute {trade_side} order for {symbol}. Please try again."
                            )
                            
                    except Exception as trade_error:
                        logger.error(f"❌ TRADE EXECUTION ERROR: {trade_error}")
                        
                        error_msg = f"❌ **Trade Execution Failed**\n\n"
                        error_msg += f"Error: {str(trade_error)}\n\n"
                        error_msg += f"**Attempted Trade:**\n"
                        error_msg += f"• {trade_side.upper()} {quantity} {symbol}\n"
                        error_msg += f"• Order Type: {order_type}\n"
                        if limit_price:
                            error_msg += f"• Limit Price: ${limit_price:.2f}\n"
                        error_msg += f"\nPlease check your inputs and try again."
                        
                        try:
                            client.chat_postEphemeral(
                                channel=channel_id,
                                user=user_id,
                                text=error_msg
                            )
                        except Exception as msg_error:
                            logger.error(f"❌ Failed to send error message: {msg_error}")
                    
                    finally:
                        loop.close()
                
                # Start trade execution in background thread
                thread = threading.Thread(target=run_trade)
                thread.daemon = True
                thread.start()
            
            # Send immediate confirmation and start background execution
            try:
                # Send ephemeral message in channel
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text=f"🔄 **Processing Trade...**\n\n"
                         f"📊 **Order Details:**\n"
                         f"• Symbol: {symbol}\n"
                         f"• Action: {trade_side.upper()}\n"
                         f"• Quantity: {quantity} shares\n"
                         f"• Order Type: {order_type.title()}\n"
                         f"{f'• Limit Price: ${limit_price:.2f}' if limit_price else ''}\n\n"
                         f"⏳ Submitting to Alpaca Paper Trading..."
                )
                
                # Execute trade in background
                execute_trade_async()
                
            except Exception as immediate_error:
                logger.error(f"❌ Immediate response error: {immediate_error}")
                # Still try to execute the trade
                execute_trade_async()
            
        except Exception as e:
            logger.error(f"❌ Error processing trade submission: {e}")
            # Send error message to user
            try:
                client.chat_postEphemeral(
                    channel="general",
                    user=body["user"]["id"],
                    text="❌ Error processing your trade. Please try again."
                )
            except:
                pass
    
    logger.info("✅ MULTI-ACCOUNT BUY/SELL COMMANDS REGISTERED SUCCESSFULLY")
    return multi_trade_command