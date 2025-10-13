#!/usr/bin/env python3
"""
Slack Bot Main Application
Entry point for the Paper Trading Slack Bot
"""
import os
import sys
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from app.config import settings
from app.handlers.commands import register_command_handlers
from app.handlers.interactions import register_interaction_handlers
from app.oms_client import oms_client

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def create_app() -> App:
    """
    Create and configure the Slack Bolt app
    
    Returns:
        Configured Slack Bolt app
    """
    logger.info("Initializing Slack Bot...")
    
    # Create Slack Bolt app
    app = App(
        token=settings.slack_bot_token,
        signing_secret=settings.slack_signing_secret
    )
    
    # Register handlers
    register_command_handlers(app)
    register_interaction_handlers(app)
    
    logger.info("Slack Bot initialized successfully")
    
    return app


def check_oms_connection():
    """Check if OMS API is reachable"""
    logger.info(f"Checking OMS API connection at {settings.oms_api_url}...")
    
    if oms_client.health_check():
        logger.info("✅ OMS API is reachable")
        return True
    else:
        logger.warning("⚠️  OMS API is not reachable - trades will fail until API is available")
        return False


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info(f"{settings.app_name} v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info("=" * 60)
    
    try:
        # Check OMS API connection
        check_oms_connection()
        
        # Create app
        app = create_app()
        
        # For development/testing with Socket Mode (doesn't require public URL)
        # Uncomment this if you have a Socket Mode token
        # handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        # logger.info("Starting bot in Socket Mode...")
        # handler.start()
        
        # For production with HTTP mode
        logger.info(f"Starting bot server on {settings.host}:{settings.port}...")
        logger.info(f"Make sure your Slack App URLs point to this server")
        logger.info("=" * 60)
        
        # Start the built-in server
        from slack_bolt.adapter.flask import SlackRequestHandler
        from flask import Flask, request
        
        flask_app = Flask(__name__)
        handler = SlackRequestHandler(app)
        
        @flask_app.route("/slack/events", methods=["POST"])
        def slack_events():
            return handler.handle(request)
        
        @flask_app.route("/slack/commands", methods=["POST"])
        def slack_commands():
            return handler.handle(request)
        
        @flask_app.route("/slack/interactions", methods=["POST"])
        def slack_interactions():
            return handler.handle(request)
        
        @flask_app.route("/health", methods=["GET"])
        def health_check():
            oms_healthy = oms_client.health_check()
            return {
                "status": "healthy",
                "service": settings.app_name,
                "version": settings.version,
                "oms_api_connected": oms_healthy
            }, 200
        
        @flask_app.route("/", methods=["GET"])
        def root():
            return {
                "service": settings.app_name,
                "version": settings.version,
                "status": "running"
            }
        
        # Run Flask app
        flask_app.run(
            host=settings.host,
            port=settings.port,
            debug=settings.debug
        )
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("Bot shutdown requested")
        logger.info("=" * 60)
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

