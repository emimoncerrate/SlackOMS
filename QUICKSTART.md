# SlackOMS - Quick Start Guide

Get your Paper Trading system up and running in minutes!

## 🎯 What You're Building

A complete paper trading system where teams can execute simulated stock trades directly from Slack:

```
User types: /trade AAPL
↓
Modal opens with trade details
↓
User fills: Quantity, GMV, BUY/SELL, Portfolio
↓
Trade executes via secure API
↓
Confirmation posted to Slack channel
```

## ⚡ Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- PostgreSQL (or use SQLite for quick testing)
- Slack Workspace (admin access)

### Step 1: Clone & Setup (5 minutes)

```bash
# Navigate to your project
cd SlackOMS

# Setup OMS API
cd oms-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-local.txt  # Use this for SQLite

# Generate API key
python generate_api_key.py
# Copy the generated key!

# Create .env file
cat > .env << 'EOF'
OMS_API_KEY=<paste-your-generated-key-here>
DATABASE_URL=sqlite:///./slackoms.db
HOST=0.0.0.0
PORT=8001
ENVIRONMENT=development
RATE_LIMIT_PER_MINUTE=60
EOF

# Start OMS API
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Step 2: Test OMS API (2 minutes)

Open a new terminal:
```bash
cd SlackOMS/oms-api

# Test health
curl http://localhost:8001/health

# Test API documentation
# Open browser: http://localhost:8001/docs

# Run test suite
source venv/bin/activate
TEST_API_URL=http://localhost:8001 python test_api.py
```

You should see: **🎉 ALL TESTS PASSED!**

### Step 3: Setup Slack Bot (10 minutes)

#### 3a. Create Slack App
1. Go to https://api.slack.com/apps
2. **Create New App** → **From scratch**
3. Name: `Paper Trading Bot`
4. Select your workspace
5. Add OAuth Scopes (OAuth & Permissions):
   - `commands`
   - `chat:write`
   - `chat:write.public`
   - `im:write`
6. Install to workspace
7. Copy **Bot Token** (xoxb-...)
8. Copy **Signing Secret** (Basic Information)

#### 3b. Configure Slack Bot

```bash
# New terminal
cd SlackOMS/slack-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env
cat > .env << 'EOF'
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your-secret-here
OMS_API_URL=http://localhost:8001
OMS_API_KEY=<same-key-from-step-1>
HOST=0.0.0.0
PORT=3000
ENVIRONMENT=development
EOF

# Edit .env with your actual tokens!
nano .env  # or vim, code, etc.
```

#### 3c. Expose Local Server (for Slack to reach you)

```bash
# Install ngrok if you haven't
# https://ngrok.com/download

# Expose port 3000
ngrok http 3000

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
```

#### 3d. Update Slack App URLs
1. Go back to your Slack App
2. **Slash Commands** → Edit `/trade`:
   - Request URL: `https://abc123.ngrok.io/slack/commands`
3. **Interactivity & Shortcuts**:
   - Request URL: `https://abc123.ngrok.io/slack/interactions`
4. **Save changes**

#### 3e. Start Bot

```bash
cd SlackOMS/slack-bot
source venv/bin/activate
python main.py
```

### Step 4: Test End-to-End! 🚀

1. Open Slack
2. Go to any channel
3. Type: `/trade AAPL`
4. Fill in the modal:
   - Symbol: AAPL
   - Quantity: 100
   - GMV: 17500.00
   - Side: BUY
   - Portfolio: My Portfolio
5. Click **Execute Trade**
6. 🎉 **You should see a confirmation message!**

## 🚀 Deploy to Production (Render - Free)

### Deploy OMS API

```bash
# Push to GitHub
git init
git add .
git commit -m "Initial commit"
git push origin main

# Follow: oms-api/DEPLOYMENT.md
# Summary:
# 1. Create PostgreSQL on Render
# 2. Create Web Service
# 3. Set environment variables
# 4. Deploy!
```

### Deploy Slack Bot

```bash
# Follow: slack-bot/DEPLOYMENT.md
# Summary:
# 1. Create Web Service on Render
# 2. Set environment variables (including OMS API URL from above)
# 3. Update Slack App URLs to Render URL
# 4. Deploy!
```

## 📚 Project Structure

```
SlackOMS/
├── README.md                  # Main project overview
├── QUICKSTART.md             # This file
│
├── oms-api/                  # Backend API
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # Database models
│   │   ├── routes.py        # API endpoints
│   │   ├── schemas.py       # Pydantic validators
│   │   ├── database.py      # Database config
│   │   ├── config.py        # Settings
│   │   ├── dependencies.py  # Security
│   │   └── utils.py         # Helper functions
│   ├── requirements.txt     # Python dependencies
│   ├── test_api.py          # Test suite
│   ├── README.md            # API documentation
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── SETUP_GUIDE.md       # Detailed setup
│
└── slack-bot/               # Slack Integration
    ├── app/
    │   ├── config.py        # Configuration
    │   ├── oms_client.py    # OMS API client
    │   ├── blocks.py        # UI components
    │   └── handlers/
    │       ├── commands.py  # Slash command handlers
    │       └── interactions.py  # Modal handlers
    ├── main.py              # Bot application
    ├── requirements.txt     # Python dependencies
    ├── README.md            # Bot documentation
    └── DEPLOYMENT.md        # Deployment guide
```

## 🔑 Key Concepts

### 1. Secure Proxy Pattern
```
Slack → Bot Server → OMS API → Database
         (validates)  (authenticates)
```

### 2. API Key Authentication
- OMS API requires `X-API-Key` header
- Bot stores this key securely
- Users never see the API key

### 3. Paper Trading
- All trades are simulated
- No real money involved
- Perfect for testing strategies

## 🐛 Common Issues & Solutions

### Port Already in Use
```bash
# Kill process on port
lsof -ti:8001 | xargs kill -9
```

### Database Connection Error
```bash
# For SQLite, just make sure the path is correct
# For PostgreSQL, verify it's running:
psql -d slackoms -c "SELECT 1"
```

### Slack "dispatch_failed" Error
- Check SLACK_SIGNING_SECRET (no typos!)
- Verify URLs don't have trailing slashes
- Check server logs for details

### Modal Doesn't Open
- Verify bot has `commands` scope
- Check SLACK_BOT_TOKEN is correct
- Look at bot server logs

## 📊 Testing Checklist

- [ ] OMS API health check passes
- [ ] OMS API test suite passes (8/8 tests)
- [ ] Bot server starts without errors
- [ ] `/trade` command opens modal
- [ ] Trade execution succeeds
- [ ] Confirmation message appears in Slack
- [ ] Trade appears in OMS API (GET /api/v1/trades)
- [ ] Portfolio summary works (GET /api/v1/portfolio/NAME)

## 🎓 Next Steps

1. **Explore the API**: Visit http://localhost:8001/docs
2. **Test different trades**: Try BUY and SELL orders
3. **Check portfolios**: Use the `/api/v1/portfolio/{name}` endpoint
4. **Deploy to production**: Follow deployment guides
5. **Add features**: See README for enhancement ideas

## 💡 Pro Tips

1. **Use meaningful portfolio names**: Group related trades together
2. **Check GMV calculation**: GMV = Quantity × Price per Share
3. **Test with small quantities first**: Verify everything works
4. **Monitor logs**: Watch for errors and warnings
5. **Keep API key secret**: Never commit `.env` files

## 📞 Need Help?

- **OMS API Issues**: Check `oms-api/SETUP_GUIDE.md`
- **Slack Bot Issues**: Check `slack-bot/README.md`
- **Deployment Issues**: See respective `DEPLOYMENT.md` files
- **General Questions**: See main `README.md`

## 🌟 You're All Set!

You now have a fully functional paper trading system integrated with Slack!

**Try these commands in Slack:**
```
/trade AAPL    - Trade Apple stock
/trade MSFT    - Trade Microsoft stock
/trade GOOGL   - Trade Google stock
```

Happy Paper Trading! 📈📉

