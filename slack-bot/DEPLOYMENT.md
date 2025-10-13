# Deployment Guide - Slack Bot to Render

This guide will walk you through deploying the Slack Bot to Render.

## Prerequisites

- ✅ OMS API deployed and running (see `../oms-api/DEPLOYMENT.md`)
- ✅ OMS API URL and API Key
- ✅ Slack Workspace (admin access)
- ✅ GitHub account
- ✅ Render account

## Step 1: Create Slack App

### 1.1 Create the App
1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. **App Name**: `Paper Trading Bot`
4. **Pick a workspace**: Select your workspace
5. Click **"Create App"**

### 1.2 Configure Bot Token Scopes
1. Go to **"OAuth & Permissions"** in the left sidebar
2. Scroll to **"Scopes"** → **"Bot Token Scopes"**
3. Add these scopes:
   - `commands` - For slash commands
   - `chat:write` - Post messages as the bot
   - `chat:write.public` - Post to channels without being invited
   - `im:write` - Send direct messages

### 1.3 Create Slash Command
1. Go to **"Slash Commands"** in the left sidebar
2. Click **"Create New Command"**
3. Fill in:
   - **Command**: `/trade`
   - **Request URL**: `https://YOUR-APP.onrender.com/slack/commands` (will update after deployment)
   - **Short Description**: `Execute a paper trade`
   - **Usage Hint**: `[SYMBOL] (e.g., /trade AAPL)`
4. Click **"Save"**

### 1.4 Enable Interactivity
1. Go to **"Interactivity & Shortcuts"** in the left sidebar
2. Toggle **"Interactivity"** to **ON**
3. **Request URL**: `https://YOUR-APP.onrender.com/slack/interactions` (will update after deployment)
4. Click **"Save Changes"**

### 1.5 Install App to Workspace
1. Go to **"Install App"** in the left sidebar
2. Click **"Install to Workspace"**
3. Review permissions and click **"Allow"**
4. **Copy the Bot User OAuth Token** (starts with `xoxb-`) - you'll need this!

### 1.6 Get Signing Secret
1. Go to **"Basic Information"** in the left sidebar
2. Scroll to **"App Credentials"**
3. **Copy the Signing Secret** - you'll need this!

## Step 2: Deploy to Render

### 2.1 Push Code to GitHub
```bash
cd /path/to/SlackOMS
git add .
git commit -m "Add Slack Bot"
git push
```

### 2.2 Create Web Service
1. Log in to Render Dashboard: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:

**Basic Settings:**
- **Name**: `slackoms-bot`
- **Region**: Same as OMS API
- **Branch**: `main`
- **Root Directory**: `slack-bot`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**:
  ```
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```
  python main.py
  ```

**Instance Type:**
- Select **Free**

### 2.3 Configure Environment Variables

Click **"Environment"** tab and add:

| Variable | Value | Where to Get It |
|----------|-------|----------------|
| `SLACK_BOT_TOKEN` | `xoxb-...` | From Step 1.5 (Install App) |
| `SLACK_SIGNING_SECRET` | `...` | From Step 1.6 (Basic Information) |
| `OMS_API_URL` | `https://slackoms-api.onrender.com` | Your deployed OMS API URL |
| `OMS_API_KEY` | Your API key | Same key from OMS API `.env` |
| `HOST` | `0.0.0.0` | Default |
| `PORT` | `$PORT` | Render auto-assigns port (use `$PORT`) |
| `ENVIRONMENT` | `production` | |
| `PYTHON_VERSION` | `3.11.0` | |

### 2.4 Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. You'll get a URL like: `https://slackoms-bot.onrender.com`
4. **Copy this URL!**

## Step 3: Update Slack App URLs

Now that you have your Render URL, update the Slack App:

### 3.1 Update Slash Command URL
1. Go back to your Slack App: https://api.slack.com/apps
2. Select your app
3. Go to **"Slash Commands"**
4. Click on `/trade` command
5. Update **Request URL** to: `https://slackoms-bot.onrender.com/slack/commands`
6. Click **"Save"**

### 3.2 Update Interactivity URL
1. Go to **"Interactivity & Shortcuts"**
2. Update **Request URL** to: `https://slackoms-bot.onrender.com/slack/interactions`
3. Click **"Save Changes"**

## Step 4: Test the Bot

### 4.1 Test Health Check
```bash
curl https://slackoms-bot.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Paper Trading Slack Bot",
  "version": "1.0.0",
  "oms_api_connected": true
}
```

### 4.2 Test in Slack
1. Open any channel in your Slack workspace
2. Type: `/trade AAPL`
3. A modal should appear!
4. Fill in the details:
   - **Quantity**: 100
   - **GMV**: 17500.00
   - **Side**: BUY
   - **Portfolio**: Test Portfolio
5. Click **"Execute Trade"**
6. You should see a confirmation message! 🎉

## Troubleshooting

### Bot doesn't respond to /trade
**Symptoms**: Nothing happens when you type `/trade`

**Solutions**:
1. Check Request URLs in Slack App match your Render URL exactly
2. Verify bot is installed in your workspace
3. Check Render logs for errors
4. Ensure SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET are correct

### Modal doesn't open
**Symptoms**: `/trade` is acknowledged but no modal appears

**Solutions**:
1. Check Render logs for errors
2. Verify SLACK_BOT_TOKEN has `commands` scope
3. Check that bot has proper permissions

### "Invalid Request" error
**Symptoms**: Slack shows "dispatch_failed" error

**Solutions**:
1. Verify SLACK_SIGNING_SECRET is correct (no typos)
2. Check server time is synchronized
3. Make sure URLs in Slack App don't have trailing slashes

### Trade execution fails
**Symptoms**: Modal submits but trade doesn't execute

**Solutions**:
1. Verify OMS_API_URL is accessible from Render
2. Check OMS_API_KEY matches the OMS API key
3. Ensure OMS API is running and healthy
4. Check Render logs for detailed error messages

### Cold Start Issues (Free Tier)
**Issue**: First request after 15 minutes takes ~30 seconds

**Solution**: This is expected on free tier. Consider:
- Upgrading to paid tier ($7/month) removes spin-down
- Or accept the delay for occasional use

## Monitoring

### Check Logs
1. Go to Render Dashboard
2. Select your `slackoms-bot` service
3. Click **"Logs"** tab
4. Watch for errors or warnings

### Check Health
```bash
# Bot health
curl https://slackoms-bot.onrender.com/health

# OMS API health (should be accessible from bot)
curl https://slackoms-api.onrender.com/health
```

## Post-Deployment Checklist

- [ ] Slack App URLs updated with Render URL
- [ ] Bot responds to `/trade` command
- [ ] Modal opens correctly
- [ ] Trade executes and posts confirmation
- [ ] OMS API connection verified
- [ ] Environment variables all set correctly
- [ ] Logs show no errors

## Security Best Practices

1. **Never share tokens**: Keep SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET private
2. **Rotate secrets**: Change OMS_API_KEY periodically
3. **Monitor logs**: Watch for unauthorized access attempts
4. **Use HTTPS only**: Render provides this automatically
5. **Verify requests**: The bot verifies all Slack requests using signing secret

## Usage in Production

### For End Users
```
/trade SYMBOL - Execute a paper trade
Example: /trade AAPL

/trade-help - Show help information
```

### Tips for Users
1. Symbol must be valid stock ticker (e.g., AAPL, MSFT, GOOGL)
2. Quantity must be positive integer
3. GMV should match: quantity × price per share
4. Choose portfolio name carefully (all trades grouped by portfolio)
5. All trades are simulated (paper trading only)

## Next Steps

- ✅ OMS API deployed and tested
- ✅ Slack Bot deployed and tested
- ➡️ Train your team on how to use `/trade`
- ➡️ Monitor for issues
- ➡️ Gather feedback and iterate

## Costs

- **Slack**: Free (up to 10 apps)
- **Render Bot**: $0/month (Free tier, with 15-min spin-down)
- **Render OMS**: $0/month (Free tier)
- **Total**: $0/month for testing

**To remove spin-down**: Upgrade both services to Starter ($7 each = $14/month)

---

**Need Help?**
- Slack API Docs: https://api.slack.com/docs
- Render Docs: https://render.com/docs
- Check Render logs for detailed errors
- Review `README.md` for local testing

