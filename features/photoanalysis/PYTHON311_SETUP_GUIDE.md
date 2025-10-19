# Python 3.11 Installation Guide for ReddyFit API

**Issue:** MediaPipe requires Python 3.11 or earlier (not compatible with Python 3.13)
**Solution:** Install Python 3.11 alongside Python 3.13

---

## Step 1: Download Python 3.11

### Option A: Direct Download (Recommended)
1. Visit: https://www.python.org/downloads/release/python-3119/
2. Scroll to "Files" section
3. Download: **Windows installer (64-bit)**
   - File: `python-3.11.9-amd64.exe`
   - Size: ~25 MB

### Option B: Using winget (Windows Package Manager)
```powershell
winget install Python.Python.3.11
```

---

## Step 2: Install Python 3.11

### Installation Steps:
1. **Run the installer** (`python-3.11.9-amd64.exe`)

2. **IMPORTANT:** On the first screen:
   - ✅ **CHECK** "Add python.exe to PATH"
   - ✅ **CHECK** "Install launcher for all users (recommended)"
   - Click **"Customize installation"**

3. **Optional Features** (check all):
   - ✅ Documentation
   - ✅ pip
   - ✅ tcl/tk and IDLE
   - ✅ Python test suite
   - ✅ py launcher
   - Click **"Next"**

4. **Advanced Options**:
   - ✅ Install for all users
   - ✅ Associate files with Python (requires the launcher)
   - ✅ Create shortcuts for installed applications
   - ✅ Add Python to environment variables
   - ✅ Precompile standard library
   - Customize install location: `C:\Python311\`
   - Click **"Install"**

5. **Wait for installation** (1-2 minutes)

6. **Disable path length limit** (click the button if shown)

7. **Close** the installer

---

## Step 3: Verify Installation

Open a **NEW** command prompt (important!) and run:

```bash
# Check Python 3.11 is installed
py -3.11 --version

# Should output: Python 3.11.9
```

If you see `Python 3.11.9`, installation was successful! ✅

---

## Step 4: Create Python 3.11 Virtual Environment

```bash
# Navigate to the project
cd C:\users\akhil\reddy\features\photoanalysis

# Create virtual environment using Python 3.11
py -3.11 -m venv venv311

# Activate the virtual environment
venv311\Scripts\activate

# Verify you're using Python 3.11
python --version
# Should output: Python 3.11.9
```

You should see `(venv311)` at the start of your command prompt.

---

## Step 5: Install Dependencies

```bash
# Make sure you're in the virtual environment (venv311 should be active)

# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify MediaPipe is installed
pip show mediapipe
```

**Expected output:**
```
Name: mediapipe
Version: 0.10.x
...
```

---

## Step 6: Start the API Server

### Method 1: Using the Setup Script
```bash
cd C:\users\akhil\reddy\features\photoanalysis
setup-python311.bat
```

### Method 2: Manual Start
```bash
# Make sure virtual environment is activated
cd C:\users\akhil\reddy

# Start the server
python -m uvicorn features.photoanalysis.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Step 7: Verify API is Running

### Open in Browser:
- **Swagger Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health

### Or Test with curl:
```bash
curl http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-17T...",
  "checks": {...}
}
```

---

## 🎉 Success!

If you see the Swagger UI page, **you're done!**

The ReddyFit Photo Analysis API is now running locally with:
- ✅ All 20 steps of the analysis pipeline
- ✅ Claude 3.5 Sonnet vision integration
- ✅ MediaPipe pose detection
- ✅ Complete REST API with 11 endpoints
- ✅ Firebase integration
- ✅ Error handling and monitoring

---

## Troubleshooting

### Issue: "py: command not found"
**Solution:** Python launcher not installed. Use `python3.11` instead of `py -3.11`

### Issue: "python --version" still shows Python 3.13
**Solution:** Make sure you activated the virtual environment first:
```bash
venv311\Scripts\activate
```

### Issue: MediaPipe installation fails
**Solution:** Verify you're using Python 3.11:
```bash
python --version  # Should be 3.11.9
pip install mediapipe --verbose
```

### Issue: Server won't start
**Solution:** Check the error logs. Common issues:
1. Make sure you're in the `reddy` directory (not `photoanalysis`)
2. Verify `.env` file exists in `reddy` directory
3. Check `firebase-credentials.json` exists

---

## Daily Usage

After initial setup, to start the server:

```bash
# 1. Navigate to project
cd C:\users\akhil\reddy\features\photoanalysis

# 2. Activate Python 3.11 virtual environment
venv311\Scripts\activate

# 3. Start server
cd ..\..
python -m uvicorn features.photoanalysis.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Or simply run:
```bash
cd C:\users\akhil\reddy\features\photoanalysis
start-api-python311.bat
```

---

## Managing Multiple Python Versions

You now have both Python 3.13 and Python 3.11 installed:

```bash
# Use Python 3.13 (your default)
python --version

# Use Python 3.11 specifically
py -3.11 --version

# Use Python 3.11 in a script
py -3.11 script.py
```

Both versions coexist peacefully. The virtual environment ensures you're using the correct version for each project.

---

## Uninstalling Python 3.11 (if needed later)

1. **Windows Settings** → **Apps** → **Python 3.11.9**
2. Click **Uninstall**
3. Delete leftover files: `C:\Python311\`

But you probably won't need to - having Python 3.11 is useful for many ML/CV projects!
