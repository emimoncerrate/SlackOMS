# SlackOMS Quick Reference Card

## 🚀 Your Deployed API

**URL**: https://slackoms-api.onrender.com

**Status**: ✅ Active (confirmed October 14, 2025)

## 🔑 Authentication

**API Key**: `a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ`

⚠️ **ACTION REQUIRED**: Verify this matches `OMS_API_KEY` in Render Dashboard

## 🧪 Quick Tests

### Health Check
```bash
curl https://slackoms-api.onrender.com/health
```

### Execute Trade
```bash
curl -X POST https://slackoms-api.onrender.com/api/v1/trade \
  -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","quantity":50,"gmv":8750.00,"side":"BUY","portfolio_name":"Test Portfolio","user_id":"U123"}'
```

### List Trades
```bash
curl https://slackoms-api.onrender.com/api/v1/trades?limit=5 \
  -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ"
```

## 🌐 Important URLs

| Resource | URL |
|----------|-----|
| API Base | https://slackoms-api.onrender.com |
| Health Check | https://slackoms-api.onrender.com/health |
| Interactive Docs | https://slackoms-api.onrender.com/docs |
| Render Dashboard | https://dashboard.render.com |

## 📋 Current Status

- [x] Phase 1.1-1.7: OMS API Built and Tested Locally
- [x] Phase 1.8: Deployed to Render
- [ ] Verify API Key in Render Dashboard
- [ ] Test Deployed API Works End-to-End
- [ ] Phase 2: Build Slack Bot

## 🎯 Next Immediate Step

1. Open Render Dashboard: https://dashboard.render.com
2. Click `slackoms-api` → **Environment** tab
3. Verify `OMS_API_KEY` = `a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ`
4. If it doesn't match, update it and wait for redeploy (~5 min)
5. Run the "Execute Trade" test above
6. ✅ When you get a successful response, you're ready for Phase 2!

## 📚 Reference Files

- `deployment_urls.txt` - Full deployment information
- `RENDER_VERIFICATION_CHECKLIST.md` - Detailed verification steps
- `oms-api/DEPLOYMENT.md` - Original deployment guide
- `QUICKSTART.md` - Getting started guide

## 🆘 Need Help?

- Check Render Logs: Dashboard → slackoms-api → Logs
- Review: `RENDER_VERIFICATION_CHECKLIST.md`
- Test Local: `cd oms-api && ./run.sh`

---

**Your Local API**: http://localhost:8001 (when running)
**Production API**: https://slackoms-api.onrender.com

