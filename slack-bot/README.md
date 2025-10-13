# Slack Bot - Paper Trading Interface

The Slack Bot provides an intuitive interface for executing paper trades directly from Slack.

## 🎯 Purpose

This bot acts as a secure intermediary between Slack users and the OMS API, allowing teams to execute simulated trades without leaving their communication platform.

## 🏗️ Architecture

**User Flow:**
1. User types `/trade AAPL` in Slack
2. Bot opens an interactive modal with trade details
3. User fills in quantity, GMV, side (BUY/SELL), portfolio
4. Bot securely calls OMS API with authentication
5. Trade executed and confirmation posted to channel

## 📋 Features

- **Slash Command**: `/trade [SYMBOL]` to initiate trades
- **Interactive Modal**: User-friendly form for trade details
- **Real-time Confirmation**: Instant feedback in Slack
- **Secure**: All API calls authenticated with secret key
- **Error Handling**: Clear error messages for users

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Slack Workspace (admin access to create apps)
- OMS API running and accessible

### Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. **App Name**: `Paper Trading Bot`
4. **Workspace**: Select your workspace
5. Click **"Create App"**

### Step 2: Configure Slack App

#### Bot Token Scopes
Go to **"OAuth & Permissions"** and add these scopes:
- `commands` - Create slash commands
- `chat:write` - Post messages to channels
- `chat:write.public` - Post to channels bot isn't in
- `im:write` - Send DMs

#### Slash Commands
Go to **"Slash Commands"** and click **"Create New Command"**:
- **Command**: `/trade`
- **Request URL**: `https://your-bot-url.com/slack/commands` (will set after deployment)
- **Short Description**: `Execute a paper trade`
- **Usage Hint**: `[SYMBOL] (e.g., /trade AAPL)`

#### Interactivity
Go to **"Interactivity & Shortcuts"**:
- Toggle **"Interactivity"** to **On**
- **Request URL**: `https://your-bot-url.com/slack/interactions`

#### Install App
Go to **"Install App"** and click **"Install to Workspace"**
- Authorize the app
- Copy the **Bot User OAuth Token** (starts with `xoxb-`)

#### App Credentials
Go to **"Basic Information"**:
- Copy the **Signing Secret**

### Step 3: Setup Local Environment

```bash
cd slack-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.template .env
# Edit .env with your credentials
```

### Step 4: Configure Environment Variables

Edit `.env`:
```env
SLACK_BOT_TOKEN=xoxb-your-actual-token
SLACK_SIGNING_SECRET=your-actual-secret
OMS_API_URL=http://localhost:8001  # or your deployed URL
OMS_API_KEY=your-oms-api-key
HOST=0.0.0.0
PORT=3000
ENVIRONMENT=development
```

### Step 5: Run the Bot

```bash
# Make sure OMS API is running first!
python main.py
```

For local development with Slack, you'll need to expose your local server using:
```bash
# Using ngrok
ngrok http 3000

# Copy the ngrok URL and update it in Slack App settings
```

## 📝 Usage

### Execute a Trade

In any Slack channel where the bot is installed:

```
/trade AAPL
```

This will open a modal where you can:
- Confirm the symbol (AAPL)
- Enter quantity (e.g., 100)
- Enter GMV (e.g., 17500.00)
- Select side (BUY or SELL)
- Enter portfolio name (e.g., "Tech Portfolio")

Click **Submit** and you'll get an instant confirmation!

### Example Confirmation Message

```
✅ Trade Executed Successfully!

Trade ID: T1697234567123
Symbol: AAPL
Side: BUY
Quantity: 100 shares
GMV: $17,500.00
Portfolio: Tech Portfolio
Executed: 2025-10-13 at 2:30 PM
```

## 🔒 Security

- **Request Verification**: All Slack requests are verified using the signing secret
- **API Key Protection**: OMS API key never exposed to users
- **Environment Variables**: All secrets stored in `.env` (not in git)
- **HTTPS Required**: Slack requires HTTPS for production (Render provides this)

## 🧪 Testing

### Test Slash Command
```bash
# In Slack, type:
/trade TEST
```

### Test Error Handling
```bash
# Try invalid symbol
/trade 123INVALID

# Try with OMS API offline
# Stop the OMS API and try /trade AAPL
```

## 📦 Deployment to Render

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

Quick steps:
1. Push code to GitHub
2. Create web service on Render
3. Set environment variables
4. Update Slack App URLs with Render URL
5. Test in Slack!

## 🐛 Troubleshooting

### Bot doesn't respond to /trade
- Check that Request URLs in Slack App settings are correct
- Verify bot is installed in your workspace
- Check server logs for errors

### Modal doesn't open
- Verify SLACK_BOT_TOKEN is correct
- Check that bot has `commands` scope
- Look for errors in server logs

### Trade execution fails
- Verify OMS_API_URL is accessible from bot server
- Check OMS_API_KEY is correct
- Ensure OMS API is running

### "Invalid Request" errors
- Verify SLACK_SIGNING_SECRET is correct
- Check system time is synced (affects signature verification)

## 📊 File Structure

```
slack-bot/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── handlers/
│   │   ├── commands.py    # Slash command handlers
│   │   ├── interactions.py # Modal submission handlers
│   │   └── messages.py    # Message formatting
│   ├── oms_client.py      # OMS API client
│   └── blocks.py          # Slack Block Kit UI
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── .env.template          # Environment variables template
├── README.md             # This file
└── DEPLOYMENT.md         # Deployment guide
```

## 🔗 Resources

- [Slack Bolt Documentation](https://slack.dev/bolt-python/)
- [Slack Block Kit Builder](https://app.slack.com/block-kit-builder)
- [OMS API Documentation](../oms-api/README.md)

## 📈 Future Enhancements

- [ ] `/portfolio [name]` - View portfolio summary
- [ ] `/trades` - List recent trades
- [ ] `/cancel [trade_id]` - Cancel a trade
- [ ] Real-time price quotes
- [ ] Trade alerts and notifications
- [ ] Portfolio performance charts

