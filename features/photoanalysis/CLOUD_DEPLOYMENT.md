# ReddyFit Photo Analysis API - Cloud Deployment Guide

**Platform**: Fly.io (Recommended)
**Status**: Production Ready ✅
**Estimated Time**: 15-20 minutes

---

## Why Fly.io?

✅ **Free tier** available (perfect for testing)
✅ **Auto-scaling** (scales to 0 when not in use = $0 cost)
✅ **Global CDN** for fast performance
✅ **Auto HTTPS** with certificates
✅ **Docker-based** (uses Python 3.11 internally)
✅ **FastAPI optimized** (officially recommended)

---

## Prerequisites

### 1. Fly.io Account
- **Sign up**: https://fly.io/app/sign-up
- **Free tier**: No credit card required
- **Verify email** after signup

### 2. Install Fly.io CLI

**Windows:**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Verify installation:**
```bash
flyctl version
```

### 3. Environment Variables

You'll need these secrets:
- ✅ `ANTHROPIC_API_KEY` (you have this)
- ✅ `FIREBASE_PROJECT_ID` (configured in .env)
- ✅ `FIREBASE_STORAGE_BUCKET` (configured in .env)

---

## Quick Deployment (Automated)

### Option 1: Using the Deploy Script (Easiest)

**Windows:**
```bash
cd C:\users\akhil\reddy\features\photoanalysis
deploy.bat
```

**Mac/Linux:**
```bash
cd /path/to/reddy/features/photoanalysis
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Check/install Fly.io CLI
2. Log you into Fly.io
3. Create the app (if needed)
4. Prompt for environment secrets
5. Deploy the Docker container
6. Test the deployment
7. Show you the live URL!

---

## Manual Deployment (Step-by-Step)

If you prefer to understand each step:

### Step 1: Navigate to Project
```bash
cd C:\users\akhil\reddy\features\photoanalysis
```

### Step 2: Login to Fly.io
```bash
flyctl auth login
```
This opens a browser for authentication.

### Step 3: Launch the App (First Time Only)
```bash
flyctl launch --name reddyfit-api --region iad --no-deploy
```

**Options:**
- `--name reddyfit-api` - Your app name (must be unique on Fly.io)
- `--region iad` - US East (Ashburn, VA) - change if needed
- `--no-deploy` - Don't deploy yet (we'll set secrets first)

**Choose:**
- PostgreSQL database? **No**
- Redis database? **No** (unless you want Redis caching)

### Step 4: Set Environment Secrets
```bash
# Set Anthropic API Key (replace with your actual key)
flyctl secrets set ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Set Firebase Configuration
flyctl secrets set FIREBASE_PROJECT_ID=reddyfit-dev
flyctl secrets set FIREBASE_STORAGE_BUCKET=reddyfit-dev.appspot.com
flyctl secrets set FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Optional: Sentry for error monitoring
# flyctl secrets set SENTRY_DSN=https://your-sentry-dsn
```

**Note:** Secrets are encrypted and never stored in code.

### Step 5: Deploy!
```bash
flyctl deploy
```

This will:
- Build Docker image with Python 3.11
- Install all dependencies (including MediaPipe)
- Push to Fly.io registry
- Deploy to production
- Start health checks

**Wait for:** "Deployment successful!"

### Step 6: Verify Deployment
```bash
# Check app status
flyctl status

# View logs
flyctl logs

# Open Swagger UI
flyctl open /api/docs
```

---

## Your App is Live! 🎉

### Access URLs

Your API is now available at:
- **Base URL**: `https://reddyfit-api.fly.dev`
- **Swagger Docs**: `https://reddyfit-api.fly.dev/api/docs`
- **Health Check**: `https://reddyfit-api.fly.dev/api/health`

Replace `reddyfit-api` with your chosen app name if different.

---

## Testing the Deployment

### 1. Health Check
```bash
curl https://reddyfit-api.fly.dev/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-17T...",
  "checks": {
    "api": "ok",
    "firestore": "ok"
  }
}
```

### 2. Swagger UI
Open in browser: `https://reddyfit-api.fly.dev/api/docs`

Try the health check endpoint:
1. Click "GET /api/health"
2. Click "Try it out"
3. Click "Execute"
4. See the response!

### 3. Create a Scan
```bash
curl -X POST "https://reddyfit-api.fly.dev/api/v1/scans" \
  -H "Authorization: Bearer mock_user_test123" \
  -F "front_image=@front.jpg" \
  -F "side_image=@side.jpg" \
  -F "back_image=@back.jpg" \
  -F "user_id=test_user" \
  -F "height_cm=178" \
  -F "gender=male"
```

---

## Managing the Deployment

### View Logs (Real-time)
```bash
flyctl logs
```

### Check App Status
```bash
flyctl status
```

### Scale the App
```bash
# Scale to 2 instances
flyctl scale count 2

# Scale back to 1
flyctl scale count 1

# Auto-scale to 0 (free tier)
flyctl scale count 0  # In fly.toml: min_machines_running = 0
```

### Update the App
After making code changes:
```bash
flyctl deploy
```

### SSH into Container
```bash
flyctl ssh console
```

### View Metrics
```bash
flyctl metrics
```

---

## Costs & Free Tier

### Free Tier Includes:
- ✅ 3 shared-CPU VMs (1GB RAM each)
- ✅ 3GB persistent storage
- ✅ 160GB outbound data transfer
- ✅ **$0/month** if you stay within limits

### How to Stay Free:
- Set `min_machines_running = 0` (already configured)
- App auto-scales to 0 when not in use
- Starts instantly when a request comes in

### If You Exceed Free Tier:
- ~$2-5/month for typical usage
- ~$0.02 per hour per machine
- Only pay for actual usage (per-second billing)

### Monitor Usage:
```bash
flyctl dashboard billing
```

---

## Troubleshooting

### Issue: "App name already taken"
**Solution:** Choose a different name:
```bash
flyctl launch --name reddyfit-api-akhil
```

### Issue: Deployment fails with "out of memory"
**Solution:** Increase RAM in `fly.toml`:
```toml
[[vm]]
  memory_mb = 2048  # Increase from 1024
```

### Issue: Health checks failing
**Solution:** Check logs:
```bash
flyctl logs
```

Common causes:
- Missing environment variables
- Firebase credentials issue
- Anthropic API key invalid

### Issue: "ModuleNotFoundError: mediapipe"
**Solution:** This shouldn't happen in Docker. If it does:
1. Check Dockerfile has all system dependencies
2. Redeploy: `flyctl deploy --no-cache`

### Issue: Slow cold starts
**Solution:** Keep 1 machine always running:
```toml
min_machines_running = 1  # In fly.toml
```

---

## Advanced Configuration

### Custom Domain

Add your own domain (e.g., `api.reddyfit.com`):

```bash
# Add certificate
flyctl certs create api.reddyfit.com

# Get DNS records
flyctl certs show api.reddyfit.com

# Add CNAME record to your DNS
# CNAME: api.reddyfit.com -> reddyfit-api.fly.dev
```

### Environment Variables (Non-Secret)

For non-sensitive config:
```bash
flyctl config set DEBUG=false APP_ENV=production
```

### Persistent Storage

If you need persistent cache:

1. Uncomment in `fly.toml`:
```toml
[[mounts]]
  source = "reddyfit_cache"
  destination = "/app/cache"
  initial_size = "1gb"
```

2. Create volume:
```bash
flyctl volumes create reddyfit_cache --size 1
```

### Multiple Regions

Deploy to multiple regions for lower latency:
```bash
flyctl regions add lax  # Los Angeles
flyctl regions add fra  # Frankfurt
```

---

## Monitoring & Observability

### Built-in Monitoring
- View in dashboard: https://fly.io/dashboard
- Real-time metrics
- Request counts
- Error rates

### Add Sentry (Optional)
```bash
# Sign up: https://sentry.io
# Get your DSN

flyctl secrets set SENTRY_DSN=https://your-sentry-dsn@sentry.io/12345
```

### Add Custom Metrics
The API already exposes Prometheus metrics at `/metrics`.

---

## Security Best Practices

### 1. Rotate API Keys Regularly
```bash
flyctl secrets set ANTHROPIC_API_KEY=new-key-here
```

### 2. Use Secrets for Sensitive Data
Never commit secrets to git:
```bash
# ✅ Good: Use flyctl secrets
flyctl secrets set API_KEY=secret

# ❌ Bad: Store in .env and commit
```

### 3. Enable Rate Limiting
Already configured in the API:
- 60 requests/minute per IP
- Configurable via environment

### 4. Monitor Logs
Set up alerts for errors:
```bash
flyctl logs --filter error
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Get your API token:
```bash
flyctl auth token
```

Add it to GitHub Secrets as `FLY_API_TOKEN`.

---

## Alternative Platforms

If you prefer a different platform:

### Railway
- Similar to Fly.io
- Simpler UI
- Connect GitHub repo → Deploy
- ~$5/month

### Google Cloud Run
- Serverless
- Pay-per-use
- Free tier: 2 million requests/month
- Slightly more complex setup

### Azure Container Apps
- If you prefer Azure
- Similar features to Fly.io
- Good integration with Azure services

---

## Support & Resources

- **Fly.io Docs**: https://fly.io/docs/
- **Community Forum**: https://community.fly.io/
- **Status Page**: https://status.flyio.net/
- **Support**: support@fly.io

---

## Next Steps

After deployment:

1. ✅ **Test all endpoints** via Swagger UI
2. ✅ **Upload real photos** and test the vision pipeline
3. ✅ **Monitor logs** for any errors
4. ✅ **Set up custom domain** (optional)
5. ✅ **Build frontend** that connects to this API
6. ✅ **Add monitoring** (Sentry, analytics)

---

**🎉 Congratulations! Your AI-powered body composition analysis API is now live and accessible from anywhere in the world!**

**Your API:** `https://reddyfit-api.fly.dev`
**Swagger Docs:** `https://reddyfit-api.fly.dev/api/docs`

Time to build the frontend! 🚀
