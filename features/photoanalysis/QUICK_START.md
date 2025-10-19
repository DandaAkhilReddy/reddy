# ReddyFit Photo Analysis API - Quick Start Guide

**🎯 Goal:** Get the API running locally in 15 minutes

---

## Option 1: Automated Setup (Easiest) ⭐

### First Time Setup:

```bash
# 1. Install Python 3.11
# Download from: https://www.python.org/downloads/release/python-3119/
# During install: CHECK "Add Python to PATH"

# 2. Run the automated setup script
cd C:\users\akhil\reddy\features\photoanalysis
setup-python311.bat

# 3. Start the server
start-api-python311.bat
```

### Daily Usage (After Setup):

```bash
cd C:\users\akhil\reddy\features\photoanalysis
start-api-python311.bat
```

---

## Option 2: Manual Setup

### First Time Setup:

```bash
# 1. Verify Python 3.11 is installed
py -3.11 --version

# 2. Create virtual environment
cd C:\users\akhil\reddy\features\photoanalysis
py -3.11 -m venv venv311

# 3. Activate virtual environment
venv311\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start server
cd ..\..
python -m uvicorn features.photoanalysis.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Daily Usage:

```bash
cd C:\users\akhil\reddy\features\photoanalysis
venv311\Scripts\activate
cd ..\..
python -m uvicorn features.photoanalysis.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Access the API

Once the server starts, open your browser:

| URL | Purpose |
|-----|---------|
| http://localhost:8000/api/docs | **Swagger UI** - Interactive API documentation |
| http://localhost:8000/api/redoc | **ReDoc** - Alternative documentation |
| http://localhost:8000/api/health | **Health Check** - Verify server is running |

---

## Test the API

### Option 1: Using Swagger UI (Easiest)
1. Open http://localhost:8000/api/docs
2. Click on any endpoint (e.g., "GET /api/health")
3. Click "Try it out"
4. Click "Execute"
5. See the response!

### Option 2: Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Detailed health check
curl http://localhost:8000/api/health/detailed

# Create a scan (requires 3 images)
curl -X POST "http://localhost:8000/api/v1/scans" \
  -H "Authorization: Bearer mock_user_test123" \
  -F "front_image=@front.jpg" \
  -F "side_image=@side.jpg" \
  -F "back_image=@back.jpg" \
  -F "user_id=test_user" \
  -F "height_cm=178"
```

---

## Available Scripts

| Script | Purpose |
|--------|---------|
| `setup-python311.bat` | **First-time setup** - Creates venv and installs dependencies |
| `start-api-python311.bat` | **Daily use** - Starts the server |
| `test-api.bat` | **Testing** - Quick health check |

---

## Troubleshooting

### Server won't start?

**Check 1:** Is Python 3.11 installed?
```bash
py -3.11 --version
```
If not: [Install Python 3.11](PYTHON311_SETUP_GUIDE.md)

**Check 2:** Is the virtual environment activated?
```bash
# You should see (venv311) in your prompt
venv311\Scripts\activate
```

**Check 3:** Are dependencies installed?
```bash
pip show mediapipe
# If error: pip install -r requirements.txt
```

**Check 4:** Is the .env file present?
```bash
# Should exist in C:\users\akhil\reddy\.env
```

### Port 8000 already in use?

```bash
# Kill the existing process
taskkill /F /IM python.exe

# Or use a different port
python -m uvicorn features.photoanalysis.api.main:app --port 8001 --reload
```

### Import errors?

Make sure you're running from the `reddy` directory (not `photoanalysis`):
```bash
cd C:\users\akhil\reddy
python -m uvicorn features.photoanalysis.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## What You Can Do with the API

### 1. Upload Photos for Body Analysis
- Upload 3 photos (front, side, back)
- Get AI-powered body measurements
- Receive body type classification
- Get confidence scores

### 2. Get AI Recommendations
- Personalized workout plans
- Nutrition recommendations
- WHOOP-integrated recovery advice

### 3. Track Progress
- View scan history
- Compare scans over time
- Track body composition changes

### 4. All Features Available
- ✅ Claude 3.5 Sonnet vision AI
- ✅ MediaPipe pose detection
- ✅ Mathematical body analysis
- ✅ Firebase data persistence
- ✅ Error monitoring
- ✅ Performance optimization

---

## Need Help?

1. **Setup Issues:** Read [PYTHON311_SETUP_GUIDE.md](PYTHON311_SETUP_GUIDE.md)
2. **API Usage:** Read [API_README.md](api/README.md)
3. **Deployment:** Read [DEPLOYMENT_STATUS.md](../../DEPLOYMENT_STATUS.md)

---

## Quick Command Reference

```bash
# Install Python 3.11
# → Download from python.org

# Setup (first time)
cd C:\users\akhil\reddy\features\photoanalysis
setup-python311.bat

# Start server (daily use)
start-api-python311.bat

# Or manual start
venv311\Scripts\activate
cd ..\..
python -m uvicorn features.photoanalysis.api.main:app --host 0.0.0.0 --port 8000 --reload

# Stop server
Ctrl + C
```

---

**🎉 That's it! You're ready to use the ReddyFit Photo Analysis API!**
