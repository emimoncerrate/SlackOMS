# 🚀 PostgreSQL Deployment Guide - Jain Global Slack Trading Bot

Complete deployment guide for the PostgreSQL-based Jain Global Slack Trading Bot with required Finnhub and Alpaca APIs.

## 🎯 Overview

This deployment uses:
- **PostgreSQL** (Render managed database) instead of DynamoDB
- **Required APIs**: Finnhub (market data) + Alpaca (paper trading)
- **HTTP Endpoints** for Slack webhook integration
- **No fallback services** - all APIs must be configured

## 📋 Prerequisites

### 1. API Keys Required
- **Slack Bot Token** (`xoxb-...`)
- **Slack Signing Secret**
- **Finnhub API Key** (free tier available at [finnhub.io](https://finnhub.io))
- **Alpaca API Keys** (free paper trading at [alpaca.markets](https://alpaca.markets))

### 2. Render Account
- Free account at [render.com](https://render.com)
- GitHub repository connected

## 🚀 Step-by-Step Deployment

### Step 1: Get API Keys

#### Finnhub API (Market Data)
1. Go to [finnhub.io](https://finnhub.io)
2. Sign up for free account
3. Get your API key from dashboard
4. Free tier: 60 calls/minute

#### Alpaca API (Paper Trading)
1. Go to [alpaca.markets](https://alpaca.markets)
2. Sign up for free account
3. Go to "Paper Trading" section
4. Generate API key and secret
5. Note: Uses paper trading URL by default

#### Slack App Setup
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Create new app → "From scratch"
3. Add OAuth scopes: `commands`, `chat:write`, `chat:write.public`
4. Install to workspace
5. Copy Bot Token (`xoxb-...`) and Signing Secret

### Step 2: Deploy to Render

#### 2a. Create PostgreSQL Database
1. In Render dashboard: **New** → **PostgreSQL**
2. **Name**: `jain-trading-db`
3. **Database**: `trading_bot`
4. **User**: `trading_user`
5. **Plan**: Free (1GB storage)
6. Click **Create Database**
7. **Copy the connection string** (DATABASE_URL)

#### 2b. Create Web Service
1. **New** → **Web Service**
2. **Connect Repository**: Select your GitHub repo
3. **Configuration**:
   - **Name**: `jain-trading-bot`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: Free

#### 2c. Set Environment Variables
In the web service **Environment** tab, add:

```bash
# Slack Configuration (Required)
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here

# Database (Required - from PostgreSQL service)
DATABASE_URL=postgresql://user:pass@host:port/db

# Market Data API (Required)
FINNHUB_API_KEY=your-finnhub-api-key

# Trading API (Required)
ALPACA_API_KEY=your-alpaca-api-key
ALPACA_SECRET_KEY=your-alpaca-secret-key

# Application Settings
ENVIRONMENT=production
PORT=8080
HOST=0.0.0.0

# Optional: Database tuning
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

#### 2d. Deploy
1. Click **Create Web Service**
2. Wait for deployment (3-5 minutes)
3. Note your service URL: `https://jain-trading-bot.onrender.com`

### Step 3: Configure Slack Commands

1. **Go to your Slack App** → **Slash Commands**
2. **Create these commands**:

#### `/trade` Command
- **Command**: `/trade`
- **Request URL**: `https://your-service.onrender.com/slack/events`
- **Description**: `Execute a paper trade`
- **Usage Hint**: `SYMBOL QUANTITY BUY/SELL`

#### `/portfolio` Command
- **Command**: `/portfolio`
- **Request URL**: `https://your-service.onrender.com/slack/events`
- **Description**: `View your portfolio`

#### `/help` Command
- **Command**: `/help`
- **Request URL**: `https://your-service.onrender.com/slack/events`
- **Description**: `Show help information`

3. **Reinstall App** to workspace

### Step 4: Test Deployment

#### 4a. Health Check
```bash
curl https://your-service.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-XX...",
  "version": "1.0.0",
  "environment": "production"
}
```

#### 4b. Test in Slack
1. Go to any Slack channel
2. Type: `/trade AAPL 100 BUY`
3. Should see trade execution with real market data
4. Type: `/portfolio` to see your positions

## 🔧 Configuration Details

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SLACK_BOT_TOKEN` | Bot OAuth token | `xoxb-123...` |
| `SLACK_SIGNING_SECRET` | Request verification | `abc123...` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` |
| `FINNHUB_API_KEY` | Market data API | `c123abc...` |
| `ALPACA_API_KEY` | Trading API key | `PK123...` |
| `ALPACA_SECRET_KEY` | Trading API secret | `abc123...` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `production` | Deployment environment |
| `PORT` | `8080` | Server port (Render managed) |
| `DB_POOL_SIZE` | `5` | Database connection pool size |
| `DB_MAX_OVERFLOW` | `10` | Max additional connections |
| `ALPACA_BASE_URL` | `https://paper-api.alpaca.markets` | Paper trading URL |

## 📊 Database Schema

The PostgreSQL database automatically creates these tables:

### Users Table
```sql
CREATE TABLE users (
    user_id VARCHAR PRIMARY KEY,
    slack_user_id VARCHAR UNIQUE NOT NULL,
    role VARCHAR NOT NULL DEFAULT 'EXECUTION_TRADER',
    profile JSONB DEFAULT '{}',
    permissions JSONB DEFAULT '[]',
    status VARCHAR DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Trades Table
```sql
CREATE TABLE trades (
    trade_id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    trade_type VARCHAR NOT NULL,
    price NUMERIC(15,4) NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'PENDING',
    risk_level VARCHAR NOT NULL DEFAULT 'MEDIUM',
    risk_analysis JSONB DEFAULT '{}',
    alpaca_order_id VARCHAR,
    executed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Positions Table
```sql
CREATE TABLE positions (
    position_id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    average_cost NUMERIC(15,4) NOT NULL DEFAULT 0,
    current_price NUMERIC(15,4) NOT NULL DEFAULT 0,
    unrealized_pnl NUMERIC(15,4) NOT NULL DEFAULT 0,
    realized_pnl NUMERIC(15,4) NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔍 Monitoring & Troubleshooting

### Health Endpoints
- **Health Check**: `https://your-service.onrender.com/health`
- **Metrics**: `https://your-service.onrender.com/metrics` (debug mode only)
- **API Docs**: `https://your-service.onrender.com/docs` (debug mode only)

### Common Issues

#### 1. Service Returns 502
- **Cause**: Service sleeping (free tier) or startup error
- **Fix**: Check logs in Render dashboard, wait 60 seconds for wake-up

#### 2. "Missing required environment variables"
- **Cause**: API keys not set correctly
- **Fix**: Verify all required environment variables in Render dashboard

#### 3. Database Connection Error
- **Cause**: DATABASE_URL incorrect or database not running
- **Fix**: Check PostgreSQL service status, verify connection string

#### 4. Slack Commands Not Working
- **Cause**: Webhook URLs not configured correctly
- **Fix**: Verify URLs in Slack app settings point to your Render service

#### 5. "Invalid API Key" Errors
- **Cause**: Finnhub or Alpaca API keys invalid
- **Fix**: Verify API keys in respective dashboards, check quotas

### Logs and Debugging
1. **Render Dashboard** → Your service → **Logs**
2. Look for startup messages and error details
3. Check database connection logs
4. Verify API key validation messages

## 💰 Cost Breakdown

### Free Tier (Recommended for Testing)
- **Render Web Service**: Free (750 hours/month, sleeps after 15min)
- **Render PostgreSQL**: Free (1GB storage)
- **Finnhub API**: Free (60 calls/minute)
- **Alpaca Paper Trading**: Free
- **Slack API**: Free
- **Total**: $0/month

### Production Tier
- **Render Web Service**: $7/month (always-on)
- **Render PostgreSQL**: $7/month (more storage/performance)
- **Finnhub API**: $0-25/month (higher limits)
- **Alpaca Paper Trading**: Free
- **Total**: ~$14-39/month

## 🎯 Features Available

### ✅ Core Trading Features
- **Real-time Market Data**: Live prices from Finnhub
- **Paper Trading**: Actual execution via Alpaca paper account
- **Portfolio Tracking**: Real-time P&L calculations
- **Risk Analysis**: Basic risk assessment for trades
- **Trade History**: Complete audit trail in PostgreSQL

### ✅ Slack Integration
- **Slash Commands**: `/trade`, `/portfolio`, `/help`
- **Interactive Modals**: Rich UI for trade entry
- **Real-time Notifications**: Trade confirmations and alerts
- **Error Handling**: User-friendly error messages

### ✅ Production Features
- **Database Persistence**: PostgreSQL with proper indexing
- **Health Monitoring**: Comprehensive health checks
- **Error Tracking**: Structured logging and metrics
- **Security**: Request validation and rate limiting

## 🚀 Next Steps

1. **Test Basic Functionality**: Verify `/trade` command works
2. **Monitor Performance**: Check Render dashboard metrics
3. **Scale if Needed**: Upgrade to paid plans for production use
4. **Add Users**: Invite team members to test
5. **Customize**: Modify trading rules and risk parameters

## 🆘 Support

- **Render Issues**: Check [Render documentation](https://render.com/docs)
- **Slack Issues**: Check [Slack API documentation](https://api.slack.com)
- **Finnhub Issues**: Check [Finnhub documentation](https://finnhub.io/docs/api)
- **Alpaca Issues**: Check [Alpaca documentation](https://alpaca.markets/docs)

## ✅ Deployment Checklist

- [ ] PostgreSQL database created on Render
- [ ] Web service deployed successfully
- [ ] All environment variables configured
- [ ] Slack app configured with correct webhook URLs
- [ ] Health check returns 200 OK
- [ ] `/trade AAPL 100 BUY` command works in Slack
- [ ] Portfolio tracking shows positions
- [ ] Real market data is being fetched
- [ ] Paper trades are executing via Alpaca

**🎉 Congratulations! Your Jain Global Slack Trading Bot is now live with PostgreSQL and real APIs! 📈**