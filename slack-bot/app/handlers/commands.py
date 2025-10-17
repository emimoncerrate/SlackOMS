"""
Slash Command Handlers
Handles /trade and other slash commands
"""
import logging
from slack_bolt import App, Ack
from slack_sdk import WebClient
from app.blocks import create_trade_modal, create_help_message

logger = logging.getLogger(__name__)

# Allowed channels where bot commands work
ALLOWED_CHANNELS = [
    "C09LMSYFH1S",  # Trading channel
]


def register_command_handlers(app: App):
    """Register all slash command handlers"""
    
    @app.command("/trade")
    def handle_trade_command(ack: Ack, command: dict, client: WebClient):
        """
        Handle /trade slash command
        
        Opens a modal for the user to enter trade details
        Optionally accepts a symbol as argument: /trade AAPL
        """
        # Acknowledge command immediately (Slack requires response within 3 seconds)
        ack()
        
        # Get channel and user info
        channel_id = command["channel_id"]
        user_id = command["user_id"]
        
        # Check if command is from allowed channel
        if channel_id not in ALLOWED_CHANNELS:
            logger.warning(f"User {user_id} tried to use /trade in unauthorized channel {channel_id}")
            try:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="⚠️ This bot is only available in the designated trading channel."
                )
            except Exception as e:
                logger.error(f"Error sending channel restriction message: {e}")
            return
        
        # Extract symbol from command text (optional)
        symbol = command.get("text", "").strip().upper()
        
        # Get trigger_id to open modal
        trigger_id = command["trigger_id"]
        
        logger.info(f"User {user_id} initiated /trade command with symbol: {symbol}")
        
        try:
            # Open modal
            modal_view = create_trade_modal(symbol=symbol, trigger_id=trigger_id)
            
            client.views_open(
                trigger_id=trigger_id,
                view=modal_view
            )
            
            logger.info(f"Trade modal opened successfully for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error opening trade modal: {str(e)}")
            
            # Send error message to user
            try:
                client.chat_postEphemeral(
                    channel=command["channel_id"],
                    user=user_id,
                    text=f"❌ Sorry, I couldn't open the trade modal. Error: {str(e)}"
                )
            except:
                pass
    
    
    @app.command("/trade-help")
    def handle_help_command(ack: Ack, command: dict, client: WebClient):
        """
        Handle /trade-help slash command
        
        Shows help information about using the bot
        """
        ack()
        
        user_id = command["user_id"]
        channel_id = command["channel_id"]
        
        # Check if command is from allowed channel
        if channel_id not in ALLOWED_CHANNELS:
            logger.warning(f"User {user_id} tried to use /trade-help in unauthorized channel {channel_id}")
            try:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="⚠️ This bot is only available in the designated trading channel."
                )
            except Exception as e:
                logger.error(f"Error sending channel restriction message: {e}")
            return
        
        logger.info(f"User {user_id} requested help")
        
        try:
            help_blocks = create_help_message()
            
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                blocks=help_blocks,
                text="Paper Trading Bot Help"
            )
            
        except Exception as e:
            logger.error(f"Error sending help message: {str(e)}")

