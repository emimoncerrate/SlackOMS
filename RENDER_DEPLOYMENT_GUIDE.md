# 🚀 Render Deployment Guide - Jain Global Slack Trading Bot

This guide will help you deploy the Jain Global Slack Trading Bot to Render.com using the **FREE tier**.

## 🎯 Quick Deploy (5 Minutes)

### Step 1: Prepare Your Slack App

1. **Create Slack App** (if not already done):
   - Go to https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Name: `Jain Trading Bot`
   - Select your workspace

2. **Configure OAuth Scopes**:
   - Go to "OAuth & Permissions"
   - Add these Bot Token Scopes:
     - `commands` (for slash commands)
     - `chat:write` (to send messages)
     - `chat:write.public` (to write in channels)

3. **Install to Workspace**:
   - Click "Install to Workspace"
   - Copy the **Bot User OAuth Token** (starts with `xoxb-`)

4. **Get Signing Secret**:
   - Go to "Basic Information"
   - Copy the **Signing Secret**

### Step 2: Deploy to Render

1. **Fork/Clone Repository**:
   ```bash
   git clone https://github.com/emimoncerrate/SlackOMS.git
   cd SlackOMS
   ```

2. **Create Render Service**:
   - Go to https://render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the `SlackOMS` repository

3. **Configure Service**:
   - **Name**: `jain-trading-bot`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r render-requirements.txt`
   - **Start Command**: `python render-app.py`
   - **Plan**: Free

4. **Set Environment Variables**:
   Click "Environment" and add:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_SIGNING_SECRET=your-signing-secret-here
   ENVIRONMENT=production
   PORT=8080
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)
   - Note your service URL: `https://jain-trading-bot.onrender.com`

### Step 3: Configure Slack Commands

1. **Add Slash Commands**:
   - Go to your Slack App → "Slash Commands"
   - Create these commands:

   **Command**: `/trade`
   - Request URL: `https://your-service.onrender.com/slack/events`
   - Description: `Execute a paper trade`
   - Usage Hint: `SYMBOL QUANTITY BUY/SELL`

   **Command**: `/portfolio`
   - Request URL: `https://your-service.onrender.com/slack/events`
   - Description: `View your portfolio`

   **Command**: `/help`
   - Request URL: `https://your-service.onrender.com/slack/events`
   - Description: `Show help information`

2. **Reinstall App**:
   - Go to "Install App"
   - Click "Reinstall to Workspace"

### Step 4: Test Your Bot! 🎉

1. Go to any Slack channel
2. Type: `/trade AAPL 100 BUY`
3. You should see a trade confirmation!

## 📊 Features Available

### ✅ Core Features (Always Available)
- **Slash Commands**: `/trade`, `/portfolio`, `/help`
- **Paper Trading**: Simulated trade execution
- **Portfolio Tracking**: Position management
- **Risk Analysis**: Basic risk assessment
- **Mock Market Data**: Realistic stock prices

### 🔧 Enhanced Features (Optional APIs)
Add these environment variables for enhanced functionality:

```bash
# Real market data (free tier available)
FINNHUB_API_KEY=your_finnhub_key

# Real paper trading
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret

# Persistent database
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 🛠️ Configuration Options

### Basic Configuration (Required)
```bash
SLACK_BOT_TOKEN=xoxb-...        # Required
SLACK_SIGNING_SECRET=...        # Required
ENVIRONMENT=production          # Required
PORT=8080                       # Required
```

### Enhanced Configuration (Optional)
```bash
# Market Data
FINNHUB_API_KEY=...            # Get free key at finnhub.io

# Paper Trading
ALPACA_API_KEY=...             # Get free paper account at alpaca.markets
ALPACA_SECRET_KEY=...

# Database (Render PostgreSQL)
DATABASE_URL=...               # Auto-provided if you add database

# AWS Services (Advanced)
AWS_ACCESS_KEY_ID=...          # For DynamoDB and Bedrock
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
```

## 🔍 Monitoring & Debugging

### Health Check
Your service health: `https://your-service.onrender.com/health`

### Logs
- View logs in Render dashboard
- Look for startup messages and error details

### Common Issues

**1. Service Returns 502**
- **Cause**: Service is sleeping (free tier)
- **Fix**: Wait 60 seconds for wake-up, or upgrade to paid plan

**2. "dispatch_failed" in Slack**
- **Cause**: Wrong webhook URL or signing secret
- **Fix**: Verify URLs in Slack app settings

**3. Commands Not Working**
- **Cause**: Missing OAuth scopes
- **Fix**: Add required scopes and reinstall app

## 🚀 Advanced Deployment

### Option 1: With PostgreSQL Database
1. In Render dashboard, create PostgreSQL database
2. Add `DATABASE_URL` environment variable
3. Redeploy service

### Option 2: With All External APIs
1. Get API keys:
   - Finnhub: https://finnhub.io (free tier)
   - Alpaca: https://alpaca.markets (free paper trading)
2. Add all environment variables
3. Redeploy service

### Option 3: Full AWS Integration
1. Set up AWS credentials
2. Create DynamoDB tables
3. Configure Bedrock access
4. Use original `app.py` instead of `render-app.py`

## 💰 Cost Breakdown

### Free Tier (Recommended for Testing)
- **Render Web Service**: Free (750 hours/month)
- **Slack API**: Free
- **Mock Services**: Free
- **Total**: $0/month

### Enhanced Tier
- **Render Web Service**: $7/month (always-on)
- **Render PostgreSQL**: $7/month
- **Finnhub API**: Free tier available
- **Alpaca Paper Trading**: Free
- **Total**: ~$14/month

### Enterprise Tier
- **AWS Services**: Variable (DynamoDB, Bedrock)
- **Premium APIs**: Variable
- **Render Pro**: $25/month
- **Total**: $50-100/month

## 🎯 Next Steps

1. **Test Basic Functionality**: Ensure `/trade` command works
2. **Add Real Market Data**: Configure Finnhub API
3. **Enable Paper Trading**: Configure Alpaca API
4. **Add Persistence**: Set up PostgreSQL database
5. **Monitor Usage**: Check Render dashboard for metrics

## 🆘 Support

- **Render Issues**: Check Render dashboard logs
- **Slack Issues**: Verify app configuration
- **Bot Issues**: Check service health endpoint
- **API Issues**: Verify API keys and quotas

## 🎉 Success Checklist

- [ ] Slack app created and configured
- [ ] Render service deployed successfully
- [ ] Environment variables set correctly
- [ ] Slash commands configured in Slack
- [ ] `/trade AAPL 100 BUY` command works
- [ ] `/portfolio` shows positions
- [ ] Health check returns 200 OK

**Congratulations! Your Jain Global Slack Trading Bot is now live! 🚀**