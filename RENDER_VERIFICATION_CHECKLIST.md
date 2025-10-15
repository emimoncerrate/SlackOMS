# Render Deployment Verification Checklist

## ✅ Service is Running
- [x] Service woke up successfully
- [x] Health endpoint returns 200 OK
- [x] Service URL: https://slackoms-api.onrender.com

## ⚠️ Environment Variables - VERIFY THESE NOW

### 1. Go to Render Dashboard
1. Navigate to: https://dashboard.render.com
2. Click on your `slackoms-api` service
3. Click the **"Environment"** tab on the left

### 2. Verify These Variables Exist and Match:

| Variable Name | Expected Value | Status |
|--------------|----------------|---------|
| `OMS_API_KEY` | `a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ` | ⬜ Check this |
| `DATABASE_URL` | (Automatically set by Render) | ⬜ Should exist |
| `ENVIRONMENT` | `production` | ⬜ Check this |
| `PYTHON_VERSION` | `3.11.0` | ⬜ Check this |

### 3. If OMS_API_KEY Doesn't Match:

**Option A: Update Render to Match Local**
1. In Render Environment tab, find `OMS_API_KEY`
2. Click "Edit"
3. Change value to: `a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ`
4. Click "Save Changes"
5. Service will redeploy automatically (wait ~5 min)

**Option B: Generate New Key for Production**
```bash
cd /Users/emily/mybuilds/SlackOMS/oms-api
python generate_api_key.py
```
Then:
1. Copy the new key
2. Update it in Render Dashboard
3. Save for Slack Bot configuration later

## 🧪 Test After Verification

Once you've verified/updated the API key, test it:

```bash
curl -X POST https://slackoms-api.onrender.com/api/v1/trade \
  -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "quantity": 50,
    "gmv": 8750.00,
    "side": "BUY",
    "portfolio_name": "Test Portfolio",
    "user_id": "U123"
  }'
```

### Expected Success Response:
```json
{
  "trade_id": "T...",
  "symbol": "AAPL",
  "quantity": 50,
  "gmv": 8750.00,
  "side": "BUY",
  "portfolio_name": "Test Portfolio",
  "user_id": "U123",
  "timestamp": "2025-10-14T...",
  "message": "Trade executed successfully"
}
```

### If You Get "Invalid API Key":
- The keys don't match
- Go back to Step 3 above

## 📊 View Your Database

After successful trades, you can query them:

```bash
# List recent trades
curl https://slackoms-api.onrender.com/api/v1/trades?limit=5 \
  -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ"

# Get portfolio summary
curl https://slackoms-api.onrender.com/api/v1/portfolio/Test%20Portfolio \
  -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ"
```

## 🎉 Success Criteria

You're ready to move on when:
- ✅ Health check returns 200 OK
- ✅ Trade execution returns 201 Created
- ✅ Trades listing works
- ✅ Portfolio summary works
- ✅ API documentation loads at /docs

## 📝 Post-Deployment Tasks

1. **Save Your Configuration**
   - See `deployment_urls.txt` for all URLs and keys
   - Keep this file secure and local only

2. **Monitor Your Service**
   - Render Dashboard > Logs tab shows real-time activity
   - Check for any errors after deployment

3. **Ready for Phase 2**
   - You now have a working OMS API
   - Next: Build Slack Bot to interact with this API
   - The Slack Bot will use: `https://slackoms-api.onrender.com`

## 🚨 Common Issues

### Issue: 502 Bad Gateway
- **Cause**: Service is sleeping (free tier)
- **Fix**: Just wait 60 seconds, service is waking up

### Issue: "Invalid API Key"
- **Cause**: Render environment variable doesn't match local
- **Fix**: Follow Step 3 in "Environment Variables" section above

### Issue: Database Connection Error
- **Cause**: DATABASE_URL not set or incorrect
- **Fix**: Ensure PostgreSQL database is linked in Render

### Issue: Build Failed
- **Cause**: Missing dependencies or Python version mismatch
- **Fix**: Check Render logs, ensure `PYTHON_VERSION=3.11.0` is set

## 🔗 Useful Links

- Render Dashboard: https://dashboard.render.com
- API Documentation: https://slackoms-api.onrender.com/docs
- Render Docs: https://render.com/docs
- Project README: ../README.md

---

**Last Updated**: October 14, 2025
**Status**: Deployment Active, API Key Verification Required
