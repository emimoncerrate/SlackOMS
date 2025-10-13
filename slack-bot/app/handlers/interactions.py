"""
Interaction Handlers
Handles modal submissions and button clicks
"""
import logging
from slack_bolt import App, Ack
from slack_sdk import WebClient
from app.oms_client import oms_client
from app.blocks import create_success_message, create_error_message

logger = logging.getLogger(__name__)


def register_interaction_handlers(app: App):
    """Register all interaction handlers"""
    
    @app.view("trade_modal_submit")
    def handle_trade_modal_submission(ack: Ack, view: dict, client: WebClient):
        """
        Handle trade modal submission
        
        Extracts trade data from modal, calls OMS API, and posts confirmation
        """
        logger.info("Processing trade modal submission")
        
        # Extract values from modal
        values = view["state"]["values"]
        user_id = view["user"]["id"]
        
        try:
            # Parse form inputs
            symbol = values["symbol_block"]["symbol_input"]["value"].strip().upper()
            quantity_str = values["quantity_block"]["quantity_input"]["value"].strip()
            gmv_str = values["gmv_block"]["gmv_input"]["value"].strip()
            side = values["side_block"]["side_select"]["selected_option"]["value"]
            portfolio = values["portfolio_block"]["portfolio_input"]["value"].strip()
            
            # Validate inputs
            errors = {}
            
            if not symbol or not symbol.isalpha():
                errors["symbol_block"] = "Symbol must contain only letters (e.g., AAPL)"
            
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    errors["quantity_block"] = "Quantity must be a positive number"
            except ValueError:
                errors["quantity_block"] = "Quantity must be a valid number"
            
            try:
                gmv = float(gmv_str)
                if gmv <= 0:
                    errors["gmv_block"] = "GMV must be a positive number"
            except ValueError:
                errors["gmv_block"] = "GMV must be a valid number (e.g., 17500.00)"
            
            if not portfolio:
                errors["portfolio_block"] = "Portfolio name cannot be empty"
            
            # If there are validation errors, return them
            if errors:
                logger.warning(f"Modal validation errors: {errors}")
                ack(response_action="errors", errors=errors)
                return
            
            # Acknowledge modal submission (closes the modal)
            ack()
            
            logger.info(f"Executing trade: {side} {quantity} {symbol} for user {user_id}")
            
            # Execute trade via OMS API
            try:
                trade_result = oms_client.execute_trade(
                    symbol=symbol,
                    quantity=quantity,
                    gmv=gmv,
                    side=side,
                    portfolio_name=portfolio,
                    user_id=user_id
                )
                
                logger.info(f"Trade executed successfully: {trade_result.get('trade_id')}")
                
                # Post success message to channel
                success_blocks = create_success_message(trade_result)
                
                # Get the channel from the view's private_metadata or use DM
                channel_id = view.get("private_metadata") or user_id
                
                client.chat_postMessage(
                    channel=channel_id,
                    blocks=success_blocks,
                    text=f"✅ Trade executed: {side} {quantity} {symbol}"
                )
                
            except Exception as e:
                logger.error(f"Trade execution failed: {str(e)}")
                
                # Post error message to user (ephemeral)
                error_blocks = create_error_message(str(e))
                
                # Try to post to channel, fallback to DM
                try:
                    channel_id = view.get("private_metadata") or user_id
                    client.chat_postEphemeral(
                        channel=channel_id,
                        user=user_id,
                        blocks=error_blocks,
                        text=f"❌ Trade failed: {str(e)}"
                    )
                except:
                    # If that fails, send DM
                    client.chat_postMessage(
                        channel=user_id,
                        blocks=error_blocks,
                        text=f"❌ Trade failed: {str(e)}"
                    )
        
        except Exception as e:
            logger.error(f"Error processing modal submission: {str(e)}", exc_info=True)
            
            # Return generic error
            ack(response_action="errors", errors={
                "symbol_block": f"An error occurred: {str(e)}"
            })

