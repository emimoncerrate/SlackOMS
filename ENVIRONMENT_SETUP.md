# 🔧 Environment Setup Guide

Quick guide to set up your environment for the Jain Global Slack Trading Bot.

## 🚀 Quick Setup (Automated)

### Option 1: Interactive Setup Script
```bash
python setup-environment.py
```
This script will guide you through setting up all required API keys and configuration.

### Option 2: Manual Setup
1. Copy the template: `cp .env.template .env`
2. Edit `.env` with your actual values
3. Validate: `python validate-environment.py`

## 📋 Required API Keys

### 1. Slack App Configuration
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Create new app → "From scratch"
3. Add OAuth scopes: `commands`, `chat:write`, `chat:write.public`
4. Install to workspace
5. Copy **Bot Token** (`xoxb-...`) and **Signing Secret**

### 2. Finnhub API (Market Data)
1. Go to [finnhub.io](https://finnhub.io)
2. Sign up for free account
3. Get API key from dashboard
4. **Free tier**: 60 calls/minute

### 3. Alpaca API (Paper Trading)
1. Go to [alpaca.markets](https://alpaca.markets)
2. Sign up for free account
3. Go to "Paper Trading" section
4. Generate **API Key** and **Secret Key**
5. **Note**: Free paper trading with $100k virtual money

## 🗄️ Database Options

### For Local Development (Recommended)
```bash
DATABASE_URL=sqlite:///./jain_trading_bot.db
```
- No setup required
- Perfect for testing
- Data stored in local file

### For Production (Render)
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
```
- Managed by Render
- Auto-provided in deployment
- Persistent and scalable

## ⚙️ Environment Variables

### Required Variables
```bash
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_SIGNING_SECRET=your-secret
DATABASE_URL=sqlite:///./jain_trading_bot.db
FINNHUB_API_KEY=your-finnhub-key
ALPACA_API_KEY=your-alpaca-key
ALPACA_SECRET_KEY=your-alpaca-secret
```

### Optional Variables
```bash
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO
DEBUG_MODE=true
```

## 🧪 Validation

### Validate Your Setup
```bash
python validate-environment.py
```

This will check:
- ✅ All required environment variables
- ✅ API key formats and validity
- ✅ Database connection
- ✅ Finnhub API connection
- ✅ Alpaca API connection

### Expected Output
```
🔍 Jain Global Slack Trading Bot - Environment Validation
======================================================================

📋 Checking Required Environment Variables...
✅ All required environment variables are set

🔧 Validating Slack Configuration...
✅ Slack configuration is valid

🔧 Validating Database Configuration...
✅ SQLite database configuration is valid

🌐 Testing Finnhub API...
✅ Finnhub API is working (AAPL price: $175.23)

🌐 Testing Alpaca API...
✅ Alpaca API is working (Account: ACTIVE, Buying Power: $100,000.00)

🌐 Testing Database Connection...
✅ SQLite database connection successful (./jain_trading_bot.db)

🎉 Environment validation PASSED! Your bot is ready to run.
```

## 🚀 Next Steps

### For Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python app.py
```

### For Render Deployment
1. Follow **POSTGRESQL_DEPLOYMENT_GUIDE.md**
2. Set environment variables in Render dashboard
3. Deploy and test

## 🔧 Troubleshooting

### Common Issues

#### "Missing required environment variables"
- **Solution**: Run `python setup-environment.py`
- **Or**: Copy `.env.template` to `.env` and fill in values

#### "Invalid Slack bot token"
- **Check**: Token starts with `xoxb-`
- **Verify**: Token is from correct Slack app
- **Regenerate**: If needed, in Slack app settings

#### "Finnhub API test failed"
- **Check**: API key is correct (no spaces)
- **Verify**: Account is active at finnhub.io
- **Rate limit**: Wait if you hit the 60/minute limit

#### "Alpaca API test failed"
- **Check**: Both API key and secret are correct
- **Verify**: Paper trading is enabled
- **Install**: `pip install alpaca-trade-api`

#### "Database connection failed"
- **SQLite**: Check file permissions and path
- **PostgreSQL**: Verify connection string format
- **Install**: `pip install psycopg2-binary` for PostgreSQL

### Getting Help

1. **Run validation**: `python validate-environment.py`
2. **Check logs**: Look for specific error messages
3. **Verify APIs**: Test keys in respective dashboards
4. **Check network**: Ensure internet connectivity

## 📁 File Structure

```
SlackOMS/
├── .env.template          # Environment template
├── .env.development       # Development defaults
├── .env                   # Your actual config (create this)
├── setup-environment.py   # Interactive setup script
├── validate-environment.py # Validation script
├── ENVIRONMENT_SETUP.md   # This guide
└── app.py                 # Main application
```

## 🎯 Ready to Deploy!

Once validation passes, you're ready to:
1. **Test locally**: `python app.py`
2. **Deploy to Render**: Follow deployment guide
3. **Configure Slack**: Set up slash commands
4. **Start trading**: Use `/trade` in Slack!

🎉 **Happy Trading!** 📈