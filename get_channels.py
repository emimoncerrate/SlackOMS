#!/usr/bin/env python3
"""
Quick script to list all channels in your Slack workspace
Run this to find channel IDs and names
"""

import os
from slack_sdk import WebClient
from dotenv import load_dotenv

# Load environment
load_dotenv()

def list_channels():
    """List all channels with their IDs and names."""
    
    # Get bot token
    token = os.getenv('SLACK_BOT_TOKEN')
    if not token:
        print("❌ SLACK_BOT_TOKEN not found in .env file")
        return
    
    # Create Slack client
    client = WebClient(token=token)
    
    try:
        print("🔍 Fetching channels from your Slack workspace...\n")
        
        # Get all channels (public and private that bot has access to)
        response = client.conversations_list(
            types="public_channel,private_channel",
            limit=100
        )
        
        if response["ok"]:
            channels = response["channels"]
            
            print(f"📋 Found {len(channels)} channels:\n")
            print("=" * 60)
            print(f"{'Channel Name':<25} {'Channel ID':<15} {'Type':<10}")
            print("=" * 60)
            
            for channel in channels:
                name = channel["name"]
                channel_id = channel["id"]
                is_private = channel.get("is_private", False)
                channel_type = "Private" if is_private else "Public"
                
                print(f"#{name:<24} {channel_id:<15} {channel_type:<10}")
            
            print("=" * 60)
            print("\n💡 To use a channel with the trading bot:")
            print("1. Copy the Channel ID from above")
            print("2. Add it to APPROVED_CHANNELS in your .env file")
            print("3. Example: APPROVED_CHANNELS=C1234567890,C0987654321")
            print("\n🔒 Recommendation: Use private channels for trading")
            
        else:
            print(f"❌ Error fetching channels: {response['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure your bot token is correct and the bot is installed in your workspace")

if __name__ == "__main__":
    list_channels()