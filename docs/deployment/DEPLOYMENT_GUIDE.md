# ReddyFit Deployment Guide

Complete guide for deploying the ReddyFit platform to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Firebase Setup](#firebase-setup)
3. [Environment Configuration](#environment-configuration)
4. [Local Development](#local-development)
5. [Production Deployment Options](#production-deployment-options)
   - [Google Cloud Run](#option-1-google-cloud-run-recommended)
   - [AWS Lambda + API Gateway](#option-2-aws-lambda--api-gateway)
   - [Docker + Kubernetes](#option-3-docker--kubernetes)
6. [Database Setup](#database-setup)
7. [API Keys & Secrets](#api-keys--secrets)
8. [Performance Optimization](#performance-optimization)
9. [Monitoring & Logging](#monitoring--logging)
10. [CI/CD Pipeline](#cicd-pipeline)

---

## Prerequisites

Before deploying ReddyFit to production, ensure you have:

- **Python 3.10+** installed locally
- **Firebase account** (free Spark plan or Blaze plan)
- **Anthropic API key** (Claude 3.5 Sonnet access)
- **OpenAI API key** (optional, for nutrition agent)
- **Git** for version control
- **Docker** (optional, for containerized deployment)
- **Google Cloud CLI** or **AWS CLI** (depending on deployment target)

---

## Firebase Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **Add Project**
3. Enter project name: `reddyfit-production` (or your choice)
4. Disable Google Analytics (optional)
5. Click **Create Project**

### 2. Enable Firestore Database

1. In Firebase Console, navigate to **Firestore Database**
2. Click **Create Database**
3. Choose **Production mode** for security
4. Select a location (choose closest to your users):
   - `us-central1` (Iowa, USA)
   - `europe-west1` (Belgium, Europe)
   - `asia-northeast1` (Tokyo, Asia)
5. Click **Enable**

### 3. Set Up Firestore Security Rules

Navigate to **Firestore Database > Rules** and add:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Scan results - authenticated users only
    match /scans/{scanId} {
      allow read: if request.auth != null && request.auth.uid == resource.data.user_id;
      allow write: if request.auth != null && request.auth.uid == request.resource.data.user_id;
    }

    // User profiles - own profile only
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // Error logs - write-only for backend
    match /error_logs/{logId} {
      allow write: if request.auth != null;
    }
  }
}
```

### 4. Enable Firebase Storage

1. Navigate to **Storage**
2. Click **Get Started**
3. Use **Production mode**
4. Choose same location as Firestore
5. Click **Done**

### 5. Set Up Storage Security Rules

Navigate to **Storage > Rules** and add:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /user-photos/{userId}/{scanId}/{imageType} {
      // Allow authenticated users to upload their own photos
      allow write: if request.auth != null && request.auth.uid == userId;

      // Allow authenticated users to read their own photos
      allow read: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

### 6. Enable Firebase Authentication

1. Navigate to **Authentication**
2. Click **Get Started**
3. Enable sign-in methods:
   - **Email/Password** (for testing)
   - **Google** (recommended for production)
   - **Anonymous** (optional, for demo users)

### 7. Generate Service Account Key

1. Navigate to **Project Settings > Service Accounts**
2. Click **Generate New Private Key**
3. Download JSON file
4. Rename to `firebase-credentials.json`
5. **NEVER commit this file to Git!**

---

## Environment Configuration

### 1. Create `.env` File

In `features/photoanalysis/`, create `.env`:

```env
# ============================================================
# ANTHROPIC CONFIGURATION
# ============================================================
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx

# ============================================================
# OPENAI CONFIGURATION (Optional - for nutrition agent)
# ============================================================
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4-turbo

# ============================================================
# FIREBASE CONFIGURATION
# ============================================================
FIREBASE_PROJECT_ID=reddyfit-production
FIREBASE_STORAGE_BUCKET=reddyfit-production.appspot.com
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# ============================================================
# REDIS CONFIGURATION (Optional - for caching)
# ============================================================
REDIS_URL=redis://localhost:6379
# For production Redis:
# REDIS_URL=redis://:password@redis-hostname:6379

# ============================================================
# API CONFIGURATION
# ============================================================
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# CORS allowed origins (comma-separated)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# ============================================================
# SENTRY CONFIGURATION (Optional - for error tracking)
# ============================================================
SENTRY_DSN=https://xxxxxxxx@sentry.io/xxxxxxx
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# ============================================================
# WHOOP INTEGRATION (Optional)
# ============================================================
WHOOP_CLIENT_ID=your_whoop_client_id
WHOOP_CLIENT_SECRET=your_whoop_client_secret
WHOOP_REDIRECT_URI=https://yourdomain.com/whoop/callback

# ============================================================
# PERFORMANCE OPTIMIZATION
# ============================================================
ENABLE_CACHING=true
CACHE_TTL_SECONDS=3600
MAX_CONCURRENT_SCANS=10
```

### 2. Secure Environment Variables

For production, **NEVER** commit `.env` files. Instead:

**Google Cloud Run:**
```bash
gcloud run deploy reddyfit-api \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-... \
  --set-env-vars FIREBASE_PROJECT_ID=reddyfit-production
```

**AWS Lambda:**
```bash
aws lambda update-function-configuration \
  --function-name reddyfit-api \
  --environment "Variables={ANTHROPIC_API_KEY=sk-ant-...,FIREBASE_PROJECT_ID=reddyfit-production}"
```

**Kubernetes:**
```bash
kubectl create secret generic reddyfit-secrets \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-... \
  --from-literal=FIREBASE_PROJECT_ID=reddyfit-production
```

---

## Local Development

### 1. Install Dependencies

```bash
cd features/photoanalysis
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Set Up Firebase Emulator (Optional)

For local development without cloud costs:

```bash
npm install -g firebase-tools
firebase login
firebase init emulators

# Select Firestore and Storage emulators
# Use default ports: Firestore (8080), Storage (9199)

firebase emulators:start
```

Update `.env` for emulator:
```env
FIREBASE_EMULATOR_HOST=localhost:8080
FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199
```

### 3. Run API Server Locally

```bash
cd features/photoanalysis
python -m api.main

# Server starts at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 4. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Create test scan (with mock auth)
curl -X POST "http://localhost:8000/api/v1/scans" \
  -H "Authorization: Bearer mock_user_test123" \
  -F "front_image=@test_front.jpg" \
  -F "side_image=@test_side.jpg" \
  -F "back_image=@test_back.jpg" \
  -F "user_id=test_user" \
  -F "height_cm=178" \
  -F "gender=male"
```

---

## Production Deployment Options

### Option 1: Google Cloud Run (Recommended)

**Pros:**
- Auto-scaling (scales to zero when idle)
- Pay only for requests
- Fully managed (no server maintenance)
- Easy HTTPS setup

**Steps:**

#### 1. Create Dockerfile

Already exists at `features/photoanalysis/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Build and Push Container

```bash
# Set project
gcloud config set project reddyfit-production

# Build container
gcloud builds submit --tag gcr.io/reddyfit-production/reddyfit-api

# Or use Docker
docker build -t gcr.io/reddyfit-production/reddyfit-api .
docker push gcr.io/reddyfit-production/reddyfit-api
```

#### 3. Deploy to Cloud Run

```bash
gcloud run deploy reddyfit-api \
  --image gcr.io/reddyfit-production/reddyfit-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  --set-env-vars FIREBASE_PROJECT_ID=reddyfit-production \
  --set-env-vars FIREBASE_STORAGE_BUCKET=reddyfit-production.appspot.com
```

#### 4. Set Up Custom Domain (Optional)

```bash
# Map domain
gcloud run domain-mappings create \
  --service reddyfit-api \
  --domain api.yourdomain.com \
  --region us-central1
```

**Cost Estimate:**
- First 2 million requests/month: FREE
- After: ~$0.40 per million requests
- Memory: ~$0.0000025 per GB-second

---

### Option 2: AWS Lambda + API Gateway

**Pros:**
- Serverless (no server management)
- Pay per request
- Scales automatically

**Steps:**

#### 1. Install Mangum (ASGI adapter)

```bash
pip install mangum
```

#### 2. Create Lambda Handler

Create `features/photoanalysis/lambda_handler.py`:

```python
from mangum import Mangum
from api.main import app

# Lambda handler
handler = Mangum(app)
```

#### 3. Package for Lambda

```bash
cd features/photoanalysis

# Create deployment package
pip install -t package -r requirements.txt
cd package
zip -r ../deployment.zip .
cd ..
zip -g deployment.zip -r api models services utils config lambda_handler.py
```

#### 4. Deploy to Lambda

```bash
# Create Lambda function
aws lambda create-function \
  --function-name reddyfit-api \
  --runtime python3.10 \
  --handler lambda_handler.handler \
  --zip-file fileb://deployment.zip \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --memory-size 2048 \
  --timeout 300 \
  --environment "Variables={ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY,FIREBASE_PROJECT_ID=reddyfit-production}"
```

#### 5. Create API Gateway

```bash
# Create REST API
aws apigateway create-rest-api --name reddyfit-api

# Configure Lambda proxy integration
# (See AWS documentation for detailed steps)
```

**Cost Estimate:**
- First 1 million requests/month: FREE
- After: ~$0.20 per million requests

---

### Option 3: Docker + Kubernetes

**Pros:**
- Full control over infrastructure
- Multi-cloud portability
- Advanced scaling strategies

**Steps:**

#### 1. Create Kubernetes Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reddyfit-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: reddyfit-api
  template:
    metadata:
      labels:
        app: reddyfit-api
    spec:
      containers:
      - name: reddyfit-api
        image: gcr.io/reddyfit-production/reddyfit-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: reddyfit-secrets
              key: ANTHROPIC_API_KEY
        - name: FIREBASE_PROJECT_ID
          value: reddyfit-production
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

#### 2. Create Service

Create `k8s/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: reddyfit-api
spec:
  type: LoadBalancer
  selector:
    app: reddyfit-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

#### 3. Deploy to Kubernetes

```bash
# Create secrets
kubectl create secret generic reddyfit-secrets \
  --from-literal=ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY

# Apply deployment
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods
kubectl get services
```

---

## Database Setup

### Firestore Collections Structure

```
📁 scans/
  📄 {scanId}
    - user_id: string
    - timestamp: timestamp
    - body_signature_id: string
    - composition_hash: string
    - measurements: map
    - ratios: map
    - aesthetic_score: map
    - confidence: map
    - image_urls: map
    - recommendations: map (optional)

📁 users/
  📄 {userId}
    - email: string
    - name: string
    - created_at: timestamp
    - scan_count: number
    - latest_scan_id: string (optional)

📁 error_logs/
  📄 {errorId}
    - error_type: string
    - step: string
    - user_id: string (optional)
    - timestamp: timestamp
    - details: map
```

### Create Firestore Indexes

For efficient queries, create indexes:

```bash
# Index for user scan history (sorted by timestamp)
gcloud firestore indexes composite create \
  --collection-group=scans \
  --field-config field-path=user_id,order=ascending \
  --field-config field-path=timestamp,order=descending

# Index for body signature search
gcloud firestore indexes composite create \
  --collection-group=scans \
  --field-config field-path=body_signature_id,order=ascending \
  --field-config field-path=timestamp,order=descending
```

---

## API Keys & Secrets

### 1. Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy key (starts with `sk-ant-api03-`)
6. **Never commit this key!**

**Usage Limits:**
- Free tier: 5 requests/minute
- Paid tier: Higher limits, pay-per-token

**Cost Estimate (Claude 3.5 Sonnet):**
- Input: $3 per million tokens
- Output: $15 per million tokens
- Average scan: ~1,500 input tokens + 500 output tokens = ~$0.012 per scan

### 2. OpenAI API Key (Optional)

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Navigate to **API Keys**
3. Create new secret key
4. Copy key (starts with `sk-`)

**Cost Estimate (GPT-4 Turbo):**
- Input: $10 per million tokens
- Output: $30 per million tokens
- Average nutrition plan: ~800 input + 600 output tokens = ~$0.026 per plan

### 3. Firebase Service Account

Already covered in [Firebase Setup](#firebase-setup) section.

---

## Performance Optimization

### 1. Enable Redis Caching

**Local (Docker):**
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

**Google Cloud (Memorystore):**
```bash
gcloud redis instances create reddyfit-cache \
  --size=1 \
  --region=us-central1 \
  --tier=basic
```

Update `.env`:
```env
REDIS_URL=redis://10.0.0.3:6379  # Use internal IP
```

### 2. Optimize Image Processing

Set environment variables:
```env
# Resize images before AI analysis
MAX_IMAGE_SIZE_MB=2
RESIZE_MAX_DIMENSION=1024

# Enable parallel processing
MAX_CONCURRENT_SCANS=10
```

### 3. Enable Response Compression

Already enabled in `api/main.py`:
```python
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 4. Configure CDN (Optional)

For serving images:
- **Google Cloud CDN**: Enable on Cloud Storage bucket
- **AWS CloudFront**: Create distribution for S3 bucket
- **Cloudflare**: Set up caching rules

---

## Monitoring & Logging

### 1. Set Up Sentry (Error Tracking)

```bash
pip install sentry-sdk
```

Update `.env`:
```env
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### 2. Google Cloud Logging

Already integrated via Cloud Run:
```bash
# View logs
gcloud run logs tail reddyfit-api --region us-central1

# Filter errors
gcloud run logs read reddyfit-api --region us-central1 --filter="severity>=ERROR"
```

### 3. Performance Monitoring

Built-in metrics available at `/api/v1/metrics`:
```bash
curl http://your-api.com/api/v1/metrics
```

Response:
```json
{
  "total_scans": 1234,
  "avg_processing_time_sec": 18.5,
  "cache_hit_rate": 0.67,
  "error_rate": 0.02
}
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          cd features/photoanalysis
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd features/photoanalysis
          python test_phase_4.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: reddyfit-production

      - name: Build container
        run: |
          cd features/photoanalysis
          gcloud builds submit --tag gcr.io/reddyfit-production/reddyfit-api

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy reddyfit-api \
            --image gcr.io/reddyfit-production/reddyfit-api \
            --platform managed \
            --region us-central1 \
            --set-env-vars ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }}
```

### Required GitHub Secrets

Add in **Settings > Secrets and variables > Actions**:

- `GCP_SA_KEY`: Base64-encoded service account JSON
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `FIREBASE_PROJECT_ID`: Your Firebase project ID

---

## Post-Deployment Checklist

- [ ] Verify health endpoints: `/health` and `/health/ready`
- [ ] Test authentication with real Firebase tokens
- [ ] Upload test photos and verify scan creation
- [ ] Check Firestore for scan data
- [ ] Verify images uploaded to Firebase Storage
- [ ] Test rate limiting (exceed limits and check 429 response)
- [ ] Monitor error rates in Sentry
- [ ] Check Cloud Logging for any errors
- [ ] Verify CORS headers for your frontend domain
- [ ] Test API documentation at `/docs`
- [ ] Run load test (e.g., with Apache Bench or Locust)
- [ ] Set up uptime monitoring (e.g., UptimeRobot, Pingdom)

---

## Troubleshooting

### Issue: "Firebase credentials not found"

**Solution:**
- Ensure `firebase-credentials.json` is in the correct path
- For Cloud Run, use service account with Firestore permissions
- Check `FIREBASE_CREDENTIALS_PATH` environment variable

### Issue: "Anthropic API rate limit exceeded"

**Solution:**
- Implement request queuing
- Enable Redis caching for duplicate requests
- Upgrade Anthropic API tier
- Add exponential backoff retry logic (already implemented)

### Issue: "Images too large for processing"

**Solution:**
- Set `MAX_IMAGE_SIZE_MB=5` in environment
- Enable automatic image resizing (already implemented)
- Return user-friendly error message

### Issue: "High latency (>30s per scan)"

**Solution:**
- Enable Redis caching
- Increase Cloud Run CPU allocation
- Optimize image preprocessing
- Parallelize independent operations (already implemented)

---

## Security Best Practices

1. **API Keys**: Never commit `.env` files. Use secret managers.
2. **Firebase Rules**: Enforce user-level access control
3. **Rate Limiting**: Prevent abuse (already implemented)
4. **HTTPS Only**: Enforce SSL/TLS in production
5. **Input Validation**: Sanitize all user inputs (already implemented)
6. **CORS**: Restrict to known frontend domains
7. **Authentication**: Always verify Firebase JWT tokens
8. **Secrets Rotation**: Rotate API keys every 90 days

---

## Support

For deployment issues:
- GitHub Issues: [github.com/DandaAkhilReddy/reddy/issues](https://github.com/DandaAkhilReddy/reddy/issues)
- Email: [Your Email]
- Documentation: [docs/](../../docs/)

---

**Last Updated:** 2025-01-17
**Maintained by:** Akhil Reddy Danda
