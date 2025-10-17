# Firebase Setup Guide for ReddyFit

Quick reference guide for setting up Firebase for the ReddyFit platform.

## 🎯 Overview

ReddyFit uses Firebase for:
- **Firestore**: NoSQL database for scan results and user data
- **Storage**: Image hosting for body scan photos
- **Authentication**: JWT-based user authentication

---

## 📋 Prerequisites

- Google account
- Firebase project (free or paid)
- Admin access to Firebase Console

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Firebase Project

1. Visit [Firebase Console](https://console.firebase.google.com/)
2. Click **Add Project**
3. Project name: `reddyfit-production`
4. Disable Google Analytics (optional)
5. Click **Create Project**

### Step 2: Enable Firestore

1. Navigate to **Build > Firestore Database**
2. Click **Create Database**
3. Mode: **Production mode**
4. Location: Choose closest to users (e.g., `us-central1`)
5. Click **Enable**

### Step 3: Enable Storage

1. Navigate to **Build > Storage**
2. Click **Get Started**
3. Mode: **Production mode**
4. Location: Same as Firestore
5. Click **Done**

### Step 4: Enable Authentication

1. Navigate to **Build > Authentication**
2. Click **Get Started**
3. Sign-in method: **Email/Password** → Enable
4. (Optional) Sign-in method: **Google** → Enable
5. Click **Save**

### Step 5: Download Service Account

1. Navigate to **Project Settings** (gear icon)
2. **Service Accounts** tab
3. Click **Generate New Private Key**
4. Save as `firebase-credentials.json`
5. **IMPORTANT: Never commit this file to Git!**

---

## 🔒 Security Rules

### Firestore Rules

Navigate to **Firestore Database > Rules** and paste:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Helper function to check authentication
    function isAuthenticated() {
      return request.auth != null;
    }

    // Helper function to check ownership
    function isOwner(userId) {
      return request.auth != null && request.auth.uid == userId;
    }

    // Scan results - users can only access their own scans
    match /scans/{scanId} {
      allow read: if isOwner(resource.data.user_id);
      allow create: if isAuthenticated() && isOwner(request.resource.data.user_id);
      allow update, delete: if isOwner(resource.data.user_id);
    }

    // User profiles - users can only access their own profile
    match /users/{userId} {
      allow read, write: if isOwner(userId);
    }

    // Error logs - backend write-only
    match /error_logs/{logId} {
      allow create: if isAuthenticated();
      allow read: if false;  // Only backend via service account
    }

    // Body signature index - public read for "find similar" feature
    match /body_signatures/{signatureId} {
      allow read: if isAuthenticated();
      allow write: if false;  // Only backend via service account
    }
  }
}
```

Click **Publish**.

### Storage Rules

Navigate to **Storage > Rules** and paste:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {

    // User photo uploads - organized by userId/scanId
    match /user-photos/{userId}/{scanId}/{imageType} {

      // Allow authenticated users to upload their own photos
      allow write: if request.auth != null
                   && request.auth.uid == userId
                   && imageType in ['front.jpg', 'side.jpg', 'back.jpg']
                   && request.resource.size < 10 * 1024 * 1024;  // 10MB limit

      // Allow authenticated users to read their own photos
      allow read: if request.auth != null && request.auth.uid == userId;
    }

    // Deny all other access
    match /{allPaths=**} {
      allow read, write: if false;
    }
  }
}
```

Click **Publish**.

---

## 📊 Firestore Data Structure

### Collections

#### `scans`

```javascript
{
  "scan_id": "uuid-here",
  "user_id": "firebase_user_id",
  "timestamp": Timestamp,
  "body_signature_id": "VTaper-BF15.5-A3F7C2-AI1.52",
  "composition_hash": "A3F7C2",

  "measurements": {
    "chest_circumference_cm": 105.0,
    "waist_circumference_cm": 82.0,
    "hip_circumference_cm": 96.0,
    "bicep_circumference_cm": 38.0,
    "thigh_circumference_cm": 58.0,
    "body_fat_percent": 14.5,
    "estimated_weight_kg": 78.0
  },

  "ratios": {
    "adonis_index": 1.52,
    "golden_ratio_deviation": 0.098,
    "symmetry_score": 82.5
  },

  "aesthetic_score": {
    "overall_score": 78.5,
    "body_type": "VTAPER"
  },

  "confidence": {
    "overall_confidence": 0.91,
    "is_reliable": true
  },

  "image_urls": {
    "front": "gs://bucket/user-photos/userId/scanId/front.jpg",
    "side": "gs://bucket/user-photos/userId/scanId/side.jpg",
    "back": "gs://bucket/user-photos/userId/scanId/back.jpg"
  },

  "whoop_data": {
    "recovery_score": 68.0,
    "strain_score": 14.2
  }
}
```

#### `users`

```javascript
{
  "user_id": "firebase_user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": Timestamp,
  "scan_count": 5,
  "latest_scan_id": "uuid-here"
}
```

#### `error_logs`

```javascript
{
  "error_id": "uuid-here",
  "timestamp": Timestamp,
  "error_type": "AIAnalysisError",
  "step": "Vision Analysis",
  "user_id": "firebase_user_id",
  "severity": "error",
  "details": {
    "message": "API timeout",
    "retries": 3
  }
}
```

---

## 🔍 Firestore Indexes

For optimal query performance, create composite indexes:

### Index 1: User Scan History

```bash
gcloud firestore indexes composite create \
  --collection-group=scans \
  --query-scope=COLLECTION \
  --field-config field-path=user_id,order=ASCENDING \
  --field-config field-path=timestamp,order=DESCENDING
```

**Purpose:** Fetch user's scans sorted by date (newest first)

### Index 2: Body Signature Lookup

```bash
gcloud firestore indexes composite create \
  --collection-group=scans \
  --query-scope=COLLECTION \
  --field-config field-path=composition_hash,order=ASCENDING \
  --field-config field-path=timestamp,order=DESCENDING
```

**Purpose:** Find similar body compositions

### Index 3: Error Log Analysis

```bash
gcloud firestore indexes composite create \
  --collection-group=error_logs \
  --query-scope=COLLECTION \
  --field-config field-path=severity,order=ASCENDING \
  --field-config field-path=timestamp,order=DESCENDING
```

**Purpose:** Monitor errors by severity

---

## 🧪 Testing Firestore Access

### Test 1: Read/Write from Python

```python
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred, {
    'projectId': 'reddyfit-production'
})

db = firestore.client()

# Write test document
doc_ref = db.collection('scans').document('test_scan')
doc_ref.set({
    'user_id': 'test_user',
    'timestamp': datetime.now(),
    'test': True
})

# Read test document
doc = doc_ref.get()
print(f"Test data: {doc.to_dict()}")

# Delete test document
doc_ref.delete()
print("Test complete!")
```

### Test 2: Storage Upload

```python
from firebase_admin import storage

# Get storage bucket
bucket = storage.bucket('reddyfit-production.appspot.com')

# Upload test image
blob = bucket.blob('user-photos/test_user/test_scan/front.jpg')
blob.upload_from_filename('test_image.jpg')

# Get public URL
url = blob.public_url
print(f"Uploaded to: {url}")

# Delete test file
blob.delete()
print("Storage test complete!")
```

---

## 💰 Cost Estimation

### Free Tier (Spark Plan)

- **Firestore:**
  - Reads: 50,000/day
  - Writes: 20,000/day
  - Deletes: 20,000/day
  - Storage: 1 GB

- **Storage:**
  - Storage: 5 GB
  - Downloads: 1 GB/day
  - Uploads: 1 GB/day

- **Authentication:**
  - 10,000 verifications/month

### Paid Tier (Blaze Plan)

**Firestore:**
- Reads: $0.06 per 100,000 documents
- Writes: $0.18 per 100,000 documents
- Storage: $0.18 per GB/month

**Storage:**
- Storage: $0.026 per GB/month
- Downloads: $0.12 per GB

**Example: 1,000 scans/month**
- Firestore: ~$0.50/month (3 writes + 10 reads per scan)
- Storage: ~$0.30/month (3 images × 2MB × 1,000 scans = 6 GB)
- **Total: ~$0.80/month**

---

## 🛠️ Environment Configuration

After Firebase setup, update your `.env`:

```env
# Firebase Configuration
FIREBASE_PROJECT_ID=reddyfit-production
FIREBASE_STORAGE_BUCKET=reddyfit-production.appspot.com
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Optional: Use emulators for local development
# FIREBASE_EMULATOR_HOST=localhost:8080
# FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199
```

---

## 🔧 Troubleshooting

### Issue: "Permission denied"

**Cause:** Security rules blocking access

**Solution:**
1. Check Firestore/Storage rules
2. Verify user authentication token
3. Ensure `user_id` matches `request.auth.uid`

### Issue: "Service account not found"

**Cause:** Missing or invalid `firebase-credentials.json`

**Solution:**
1. Re-download service account key from Firebase Console
2. Check file path in `FIREBASE_CREDENTIALS_PATH`
3. Verify file is valid JSON

### Issue: "Quota exceeded"

**Cause:** Exceeded free tier limits

**Solution:**
1. Upgrade to Blaze plan
2. Optimize queries (reduce reads/writes)
3. Enable caching for repeated reads

### Issue: "Index required for query"

**Cause:** Missing composite index

**Solution:**
1. Copy index creation link from error message
2. Click to auto-create index in Firebase Console
3. Wait 2-5 minutes for index to build

---

## 📚 Additional Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Best Practices](https://firebase.google.com/docs/firestore/best-practices)
- [Storage Security Rules](https://firebase.google.com/docs/storage/security)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)

---

**Last Updated:** 2025-01-17
**Maintained by:** Akhil Reddy Danda
