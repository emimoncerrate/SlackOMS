# Debug: Slack Modal Not Appearing

## ✅ What We Know:

1. **Command is being received** - You see logs/database activity
2. **Modal is NOT appearing** - Nothing shows up in Slack UI
3. **Bot is processing the command** - But not sending the modal back

---

## 🔍 Most Likely Causes:

### 1. Bot Token Issues
**Problem**: Wrong OAuth token or missing permissions
**Check**: Make sure `SLACK_BOT_TOKEN` in Render environment variables is correct

### 2. Render Logs Show Errors
**Problem**: Bot is crashing when trying to open modal
**Check**: Need to see Render logs to find the exact error

### 3. Trigger ID Expired
**Problem**: Taking too long to respond (>3 seconds)
**Check**: Logs should show timing

---

## 🛠️ Immediate Actions:

### Action 1: Check Render Logs

1. Go to: https://dashboard.render.com
2. Click on your **Slack Bot service** (trade-simulation-bot or similar)
3. Click **"Logs"** tab
4. Clear logs or scroll to bottom
5. In Slack, type: `/trade AAPL`
6. Watch the logs in real-time

**What to look for:**
```
✅ GOOD:
INFO: 127.0.0.1 - "POST /slack/commands HTTP/1.1" 200 OK
User U123 initiated /trade command with symbol: AAPL
Trade modal opened successfully for user U123

❌ BAD (shows error):
ERROR: Error opening trade modal: [error message]
```

### Action 2: Test Bot Health

```bash
curl https://[your-bot-url].onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "SlackOMS Bot", 
  "oms_api_connected": true
}
```

### Action 3: Verify Environment Variables in Render

Go to Render → Your bot service → Environment tab

Make sure these exist:
- `SLACK_BOT_TOKEN` - Should start with `xoxb-`
- `SLACK_SIGNING_SECRET` - 32 character hex string
- `OMS_API_URL` - `https://slackoms-api.onrender.com`
- `OMS_API_KEY` - Your API key
- `ENVIRONMENT` - `production`

---

## 🎯 Quick Tests:

### Test 1: Is Bot Service Running?

```bash
# Replace with your actual bot URL
curl https://trade-simulation-bot.onrender.com/health
```

### Test 2: Check Slack App Permissions

1. Go to: https://api.slack.com/apps
2. Click your app
3. Go to **"OAuth & Permissions"**
4. Make sure these scopes are present:
   - `commands` - Use slash commands
   - `chat:write` - Send messages
   - `users:read` - Read user info (optional)
   
### Test 3: Reinstall App (if permissions changed)

1. Same app → **"Install App"**
2. Click **"Reinstall App"**
3. Click **"Allow"**

---

## 📝 Tell Me:

To debug this, I need to know:

1. **What's your bot service URL?** (from Render dashboard)
2. **What do the Render logs show** when you type `/trade AAPL`?
3. **Does the health check work?** Run:
   ```bash
   curl https://[bot-url]/health
   ```

---

## 🚨 Common Errors & Fixes:

### Error: "invalid_trigger"
**Cause**: Trigger ID expired (took >3 seconds to respond)
**Fix**: Bot is too slow - probably sleeping on free tier

**Solution**: Wake up the bot first:
```bash
# Wake up bot
curl https://[bot-url]/health
# Wait 30 seconds
# Then try /trade in Slack
```

### Error: "not_authed" or "invalid_auth"
**Cause**: Wrong `SLACK_BOT_TOKEN`
**Fix**: 
1. Go to https://api.slack.com/apps → Your App → "OAuth & Permissions"
2. Copy the **Bot User OAuth Token** (starts with `xoxb-`)
3. Update `SLACK_BOT_TOKEN` in Render environment variables
4. Manually deploy or restart service

### Error: "missing_scope"
**Cause**: App doesn't have required permissions
**Fix**:
1. Go to https://api.slack.com/apps → Your App → "OAuth & Permissions"
2. Add missing scope under "Bot Token Scopes"
3. Reinstall app

### Error: Connection timeout
**Cause**: Bot service is down or sleeping
**Fix**: Wake it up with health check, or upgrade from free tier

---

## 🎉 Expected Behavior:

When working correctly:

1. You type: `/trade AAPL` in Slack
2. **Immediately** (< 1 second), a modal pops up
3. Modal looks like the screenshot you shared:
   - Stock Symbol: AAPL
   - Buy/Sell radio buttons
   - Quantity field
   - GMV field
   - Order Type dropdown
   - Execute Trade button

---

## Next Steps:

**Tell me your bot URL and what you see in Render logs, and I'll help you fix it!** 🚀

Example of bot URL:
- `https://trade-simulation-bot.onrender.com`
- `https://slackoms-bot.onrender.com`
- `https://paper-trading-bot.onrender.com`

