# 🤖 Phase 2: Slack Bot - Action Plan

**Goal**: Connect Slack to your OMS API so you can execute trades with `/trade AAPL 50`

**Status**: ✅ Code Complete | 🚧 Deployment Needed  
**Estimated Time**: 30-45 minutes

---

## 📋 What You'll Accomplish

By the end of Phase 2, you'll be able to:
- Type `/trade AAPL 50` in any Slack channel
- See a nice form pop up to fill in trade details
- Click "Submit" and see a confirmation message
- View the trade in your OMS API

---

## 🎯 The 4 Steps

```
Step 1: Create Slack App (15 min)
   ↓
Step 2: Deploy Bot to Render (10 min)
   ↓
Step 3: Connect Slack → Bot (5 min)
   ↓
Step 4: Test It! (5 min)
```

---

## Step 1: Create Slack App & Get Credentials 🔑

**What you're doing**: Setting up a new app in Slack and getting 2 secret keys

### Actions:

1. **Go to Slack API Dashboard**
   - Open: https://api.slack.com/apps
   - Click **"Create New App"** → **"From scratch"**

2. **Name Your App**
   - **App Name**: `Paper Trading Bot`
   - **Workspace**: Choose your workspace
   - Click **"Create App"**

3. **Add Bot Permissions**
   - Go to **"OAuth & Permissions"** (left sidebar)
   - Scroll to **"Bot Token Scopes"**
   - Click **"Add an OAuth Scope"** and add:
     - `commands` ← Let bot use slash commands
     - `chat:write` ← Let bot send messages
     - `chat:write.public` ← Let bot post anywhere
     - `im:write` ← Let bot send DMs

4. **Create the /trade Command**
   - Go to **"Slash Commands"** (left sidebar)
   - Click **"Create New Command"**
   - Fill in:
     - **Command**: `/trade`
     - **Request URL**: `https://TEMP.com/slack/commands` (we'll update this later)
     - **Short Description**: `Execute a paper trade`
     - **Usage Hint**: `AAPL 50`
   - Click **"Save"**

5. **Enable Interactivity** (for the modal form)
   - Go to **"Interactivity & Shortcuts"** (left sidebar)
   - Toggle **ON**
   - **Request URL**: `https://TEMP.com/slack/interactions` (we'll update this later)
   - Click **"Save Changes"**

6. **Install to Workspace**
   - Go to **"Install App"** (left sidebar)
   - Click **"Install to Workspace"**
   - Click **"Allow"**
   - **🔑 COPY THE BOT TOKEN** (starts with `xoxb-`)
     - Save it somewhere! You'll need it in Step 2

7. **Get Signing Secret**
   - Go to **"Basic Information"** (left sidebar)
   - Scroll to **"App Credentials"**
   - **🔑 COPY THE SIGNING SECRET**
     - Save it somewhere! You'll need it in Step 2

### ✅ What You Should Have Now:
- [ ] Slack app created
- [ ] Bot Token (xoxb-...) copied
- [ ] Signing Secret copied
- [ ] `/trade` command created (with temp URL)
- [ ] Interactivity enabled (with temp URL)

---

## Step 2: Deploy Bot to Render ☁️

**What you're doing**: Putting your Slack bot code on Render's servers

### Actions:

1. **Go to Render Dashboard**
   - Open: https://dashboard.render.com
   - Click **"New +"** → **"Web Service"**

2. **Connect Your Repository**
   - If you haven't already:
     - Push your code to GitHub first
     - Connect your GitHub account to Render
   - Select your `SlackOMS` repository

3. **Configure Service Settings**

   **Basic Info:**
   - **Name**: `slackoms-bot`
   - **Region**: Same as your OMS API (check your OMS API region)
   - **Branch**: `main`
   - **Root Directory**: `slack-bot` ← IMPORTANT!
   - **Runtime**: `Python 3`

   **Build & Deploy:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

   **Instance Type:**
   - Select **Free** (same as OMS API)

4. **Add Environment Variables**

   Click **"Advanced"** → Add these environment variables:

   | Variable Name | Value | Where to Get It |
   |---------------|-------|----------------|
   | `SLACK_BOT_TOKEN` | `xoxb-...` | From Step 1.6 |
   | `SLACK_SIGNING_SECRET` | Your signing secret | From Step 1.7 |
   | `OMS_API_URL` | `https://slackoms-api.onrender.com` | Your OMS API URL |
   | `OMS_API_KEY` | `a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ` | Your API key |
   | `ENVIRONMENT` | `production` | Type this exactly |

5. **Deploy!**
   - Click **"Create Web Service"**
   - Wait 5-10 minutes for deployment
   - Watch the logs for `Running on http://0.0.0.0:5000`

### ✅ What You Should Have Now:
- [ ] Bot service deployed on Render
- [ ] Bot URL: `https://slackoms-bot.onrender.com`
- [ ] Environment variables set
- [ ] Service shows "Active" status

---

## Step 3: Connect Slack to Your Bot 🔗

**What you're doing**: Telling Slack where your bot lives

### Actions:

1. **Update Slash Command URL**
   - Go back to https://api.slack.com/apps
   - Select your **"Paper Trading Bot"**
   - Go to **"Slash Commands"**
   - Click on `/trade` to edit
   - Change **Request URL** to: `https://slackoms-bot.onrender.com/slack/commands`
   - Click **"Save"**

2. **Update Interactivity URL**
   - Go to **"Interactivity & Shortcuts"**
   - Change **Request URL** to: `https://slackoms-bot.onrender.com/slack/interactions`
   - Click **"Save Changes"**

3. **Reinstall App** (if needed)
   - Go to **"Install App"**
   - If you see "Reinstall App", click it
   - Click **"Allow"**

### ✅ What You Should Have Now:
- [ ] Slash command points to your Render bot URL
- [ ] Interactivity points to your Render bot URL
- [ ] App reinstalled (if prompted)

---

## Step 4: Test Your Bot! 🎉

**What you're doing**: Making your first trade from Slack!

### Actions:

1. **Open Slack**
   - Go to any channel or DM

2. **Type the Command**
   ```
   /trade AAPL
   ```
   - Press Enter

3. **Fill Out the Modal**
   A form should pop up! Fill it in:
   - **Symbol**: AAPL (already filled)
   - **Quantity**: 50
   - **GMV**: 8750.00
   - **Side**: BUY
   - **Portfolio Name**: Tech Portfolio
   - **User ID**: Your username

4. **Submit**
   - Click **"Execute Trade"**
   - You should see a success message!

5. **Verify in OMS API**
   ```bash
   curl "https://slackoms-api.onrender.com/api/v1/trades?limit=5" \
     -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ"
   ```
   - You should see your trade!

### ✅ Success Indicators:
- [ ] `/trade` command works in Slack
- [ ] Modal appears when you run command
- [ ] Submit button works
- [ ] Confirmation message appears
- [ ] Trade shows up in OMS API

---

## 🚨 Troubleshooting

### "dispatch_failed" error
- **Cause**: Render bot not running or wrong URL
- **Fix**: Check Render logs, verify URLs in Slack settings

### Modal doesn't appear
- **Cause**: Interactivity URL not set correctly
- **Fix**: Double-check Step 3.2, make sure URL ends with `/slack/interactions`

### "Invalid API Key" in bot logs
- **Cause**: Wrong OMS_API_KEY environment variable
- **Fix**: Check Render environment variables match your OMS API key

### Bot responds slowly
- **Cause**: Free tier spin-down
- **Fix**: Normal! First request takes ~60 seconds, then fast

---

## 📚 Reference Information

### Your URLs:
- **OMS API**: https://slackoms-api.onrender.com
- **Slack Bot**: https://slackoms-bot.onrender.com
- **Slack Apps**: https://api.slack.com/apps

### Your Credentials:
- **OMS API Key**: `a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ`
- **Slack Bot Token**: (you copied this in Step 1.6)
- **Slack Signing Secret**: (you copied this in Step 1.7)

### Documentation:
- Full guide: `slack-bot/DEPLOYMENT.md`
- Quick reference: `QUICK_REFERENCE.md`

---

## 🎯 Current Status

- [x] Phase 0: Project Setup
- [x] Phase 1: OMS API Deployed
- [ ] **Phase 2.1**: Create Slack App ← YOU ARE HERE
- [ ] Phase 2.2: Deploy to Render
- [ ] Phase 2.3: Configure Webhooks
- [ ] Phase 2.4: Test in Slack

---

## 🚀 Let's Start!

**Ready to begin?**

1. Open https://api.slack.com/apps in a new tab
2. Have a notepad ready to save your tokens
3. Follow Step 1 above

**Estimated time to first trade**: 30-45 minutes

**Need help?** Each step has detailed instructions in `slack-bot/DEPLOYMENT.md`

---

*Last Updated: October 14, 2025*  
*Next: Create Slack App & Get Credentials*

