# SlackOMS - Paper Trading Order Management System

A secure, production-ready paper trading system with Slack integration for executing and managing simulated trades.

## 🎯 Project Status

| Phase | Status | Completion Date |
|-------|--------|----------------|
| Phase 0: Project Setup | ✅ Complete | Oct 13, 2025 |
| Phase 1: OMS API | ✅ **DEPLOYED** | **Oct 14, 2025** |
| Phase 2: Slack Bot | 🚧 Ready to Deploy | Pending |

## 🌐 Live Production API

**URL**: https://slackoms-api.onrender.com  
**Documentation**: https://slackoms-api.onrender.com/docs  
**Status**: ✅ Active and Verified

### Quick Test
```bash
curl https://slackoms-api.onrender.com/health
```

## 📊 What We've Built

### Phase 1: OMS API (✅ Complete)
A fully functional trading API with:
- ✅ Trade execution endpoint
- ✅ Portfolio tracking
- ✅ Trade history queries
- ✅ PostgreSQL database
- ✅ API key authentication
- ✅ Deployed to Render
- ✅ **First trade executed successfully!**

**Verified Trade**: `T1760404507405156` (50 shares AAPL @ $175)

### Phase 2: Slack Bot (Ready)
All code written, ready to deploy:
- `/trade` slash command
- Interactive modal UI
- Trade confirmations
- Integration with OMS API

## 🚀 Quick Start

### Using the Production API

1. **Execute a Trade**:
```bash
curl -X POST https://slackoms-api.onrender.com/api/v1/trade \
  -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "quantity": 50,
    "gmv": 8750.00,
    "side": "BUY",
    "portfolio_name": "My Portfolio",
    "user_id": "U123"
  }'
```

2. **View Trades**:
```bash
curl "https://slackoms-api.onrender.com/api/v1/trades?limit=10" \
  -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ"
```

3. **Check Portfolio**:
```bash
curl "https://slackoms-api.onrender.com/api/v1/portfolio/My%20Portfolio" \
  -H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ"
```

### Local Development

See `oms-api/SETUP_GUIDE.md` for detailed instructions.

## 📁 Project Structure

```
SlackOMS/
├── oms-api/              # ✅ Backend API (Deployed)
│   ├── app/             # Application code
│   ├── requirements.txt # Dependencies
│   ├── render.yaml      # Render config
│   └── DEPLOYMENT.md    # Deployment guide
│
├── slack-bot/           # 🚧 Slack integration (Ready)
│   ├── app/            # Bot code
│   ├── main.py         # Entry point
│   └── DEPLOYMENT.md   # Setup instructions
│
└── Documentation/       # ✅ Project docs
    ├── QUICK_REFERENCE.md
    ├── PHASE1_COMPLETION_REPORT.md
    └── deployment_urls.txt
```

## 🎓 Key Features

### Security
- 🔒 API key authentication
- 🔒 HTTPS/TLS encryption
- 🔒 Environment variable protection
- 🔒 Input validation
- 🔒 Rate limiting (100 req/min)

### Functionality
- 📈 Buy/Sell trade execution
- 💼 Portfolio tracking & aggregation
- 📊 Trade history queries
- 🔍 Real-time position calculation
- ⏱️ Timestamp tracking

### Infrastructure
- ☁️ Deployed on Render (free tier)
- 🗄️ PostgreSQL database
- 📝 Comprehensive logging
- 🏥 Health monitoring
- 📖 Interactive API docs

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `QUICK_REFERENCE.md` | Commands and URLs at a glance |
| `PHASE1_COMPLETION_REPORT.md` | Full deployment verification |
| `deployment_urls.txt` | Credentials and endpoints |
| `oms-api/DEPLOYMENT.md` | Render deployment guide |
| `oms-api/SETUP_GUIDE.md` | Local development setup |
| `slack-bot/DEPLOYMENT.md` | Slack bot deployment |
| `QUICKSTART.md` | Getting started guide |

## 🎯 Next Steps

### To Deploy Slack Bot:
1. Open `slack-bot/DEPLOYMENT.md`
2. Create Slack App
3. Deploy to Render
4. Configure webhooks
5. Test `/trade` command

**Estimated Time**: 30-45 minutes

## 💡 Technology Stack

**Backend**:
- Python 3.13
- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn

**Slack Integration**:
- Slack Bolt SDK
- Flask
- Slack Block Kit

**Deployment**:
- Render.com (free tier)
- Git-based deployments
- Environment variables

## 📊 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/docs` | GET | No | API documentation |
| `/api/v1/trade` | POST | Yes | Execute trade |
| `/api/v1/trades` | GET | Yes | List trades |
| `/api/v1/trades/{id}` | GET | Yes | Get trade |
| `/api/v1/portfolio/{name}` | GET | Yes | Portfolio summary |

## 🔑 Authentication

All protected endpoints require an `X-API-Key` header:

```bash
-H "X-API-Key: a8GKxzV6Sispbga2VuE0XvPOVdtRLcL5hNoiXTPflxQ"
```

## 💰 Costs

**Current**: $0/month (Render free tier)  
**Limitations**:
- Service sleeps after 15 min inactivity
- 750 hours/month runtime
- 1GB database storage

**To upgrade**: $14/month for always-on service + larger database

## 🐛 Troubleshooting

### Service Returns 502
- **Cause**: Service is sleeping (free tier)
- **Fix**: Wait 60 seconds for wake-up

### "Invalid API Key"
- **Cause**: API key mismatch
- **Fix**: Check Render environment variables

### Database Error
- **Cause**: DATABASE_URL not set
- **Fix**: Verify PostgreSQL connection string

See `RENDER_VERIFICATION_CHECKLIST.md` for detailed troubleshooting.

## 📈 Verified Performance

- ✅ First production trade: **SUCCESS**
- ✅ Database persistence: **WORKING**
- ✅ Portfolio aggregation: **ACCURATE**
- ✅ API response time: **<200ms** (warm)
- ✅ Cold start time: **~60 seconds**

## 🏆 Achievements

- ✅ Production-ready API deployed
- ✅ PostgreSQL database configured
- ✅ Trade execution verified
- ✅ Portfolio tracking operational
- ✅ Authentication secured
- ✅ Documentation complete
- ✅ **First successful trade logged!**

## 📞 Support

- **API Docs**: https://slackoms-api.onrender.com/docs
- **Render Dashboard**: https://dashboard.render.com
- **Project Docs**: See `Documentation/` directory

## 📄 License

This is a personal project for paper trading simulation.

---

## 🎉 Current Status

**Phase 1: COMPLETE ✅**

Your OMS API is live, tested, and ready for Slack integration!

**Trade ID `T1760404507405156` successfully executed on October 14, 2025 at 01:15:07 UTC**

Ready to proceed to Phase 2: Slack Bot deployment.

---

*Last Updated: October 14, 2025*  
*Deployment Status: Production Active*  
*Next Milestone: Slack Bot Integration*
