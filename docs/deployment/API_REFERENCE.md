# ReddyFit API Reference

Complete REST API documentation for the ReddyFit platform.

## Base URL

**Production:** `https://api.reddyfit.com` (example)
**Local Development:** `http://localhost:8000`

## API Version

Current version: `v1`

All endpoints are prefixed with `/api/v1`

---

## Authentication

All endpoints (except health checks) require Firebase JWT authentication.

### Headers

```http
Authorization: Bearer <FIREBASE_JWT_TOKEN>
```

### Getting a Token

**Using Firebase SDK (JavaScript):**

```javascript
import { getAuth } from 'firebase/auth';

const auth = getAuth();
const user = auth.currentUser;
const token = await user.getIdToken();

// Use token in API requests
fetch('https://api.reddyfit.com/api/v1/scans', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

**Using Firebase Admin SDK (Python):**

```python
from firebase_admin import auth

# Verify token server-side
decoded_token = auth.verify_id_token(token)
user_id = decoded_token['uid']
```

---

## Rate Limiting

- **Per User:** 60 requests/minute
- **Per IP:** 1000 requests/hour

Rate limit headers included in responses:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705449600
```

**429 Too Many Requests** response when exceeded:

```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds."
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message here",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-01-17T12:00:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid auth token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 413 | Payload Too Large | File size exceeds limit |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary outage |

---

## Endpoints

### Health Check

#### `GET /health`

Check API health status.

**Authentication:** Not required

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-01-17T12:00:00Z",
  "version": "1.0.0"
}
```

---

#### `GET /health/ready`

Check if API is ready to serve requests (Kubernetes readiness probe).

**Authentication:** Not required

**Response:**

```json
{
  "status": "ready",
  "database": "connected",
  "ai_service": "available"
}
```

---

### Scan Management

#### `POST /api/v1/scans`

Create a new body scan from uploaded photos.

**Authentication:** Required

**Request:**

- **Content-Type:** `multipart/form-data`
- **Body Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `front_image` | File | Yes | Front-facing photo (JPG/PNG, max 10MB) |
| `side_image` | File | Yes | Side-facing photo (JPG/PNG, max 10MB) |
| `back_image` | File | Yes | Back-facing photo (JPG/PNG, max 10MB) |
| `user_id` | String | Yes | Firebase user ID |
| `height_cm` | Float | Yes | User height in centimeters (100-250) |
| `weight_kg` | Float | No | User weight in kilograms (30-300) |
| `age` | Integer | No | User age (13-120) |
| `gender` | String | No | User gender (`male`, `female`, `other`) |

**Example (cURL):**

```bash
curl -X POST "https://api.reddyfit.com/api/v1/scans" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -F "front_image=@front.jpg" \
  -F "side_image=@side.jpg" \
  -F "back_image=@back.jpg" \
  -F "user_id=firebase_user_123" \
  -F "height_cm=178" \
  -F "weight_kg=75" \
  -F "age=28" \
  -F "gender=male"
```

**Response (201 Created):**

```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "body_signature_id": "VTaper-BF14.5-A3F7C2-AI1.52",
  "user_id": "firebase_user_123",
  "timestamp": "2025-01-17T12:00:00Z",

  "measurements": {
    "chest_circumference_cm": 105.0,
    "waist_circumference_cm": 82.0,
    "hip_circumference_cm": 96.0,
    "bicep_circumference_cm": 38.0,
    "thigh_circumference_cm": 58.0,
    "calf_circumference_cm": 38.0,
    "shoulder_width_cm": 48.0,
    "body_fat_percent": 14.5,
    "estimated_weight_kg": 78.0
  },

  "ratios": {
    "shoulder_to_waist_ratio": 1.52,
    "adonis_index": 1.52,
    "golden_ratio_deviation": 0.098,
    "waist_to_hip_ratio": 0.85,
    "symmetry_score": 82.5
  },

  "aesthetic_score": {
    "overall_score": 78.5,
    "golden_ratio_score": 34.0,
    "symmetry_score": 25.0,
    "body_type": "VTAPER",
    "body_type_confidence": 0.88
  },

  "confidence": {
    "overall_confidence": 0.91,
    "is_reliable": true
  },

  "image_urls": {
    "front": "https://storage.googleapis.com/...",
    "side": "https://storage.googleapis.com/...",
    "back": "https://storage.googleapis.com/..."
  },

  "processing_time_sec": 18.5,
  "api_version": "2.0"
}
```

**Error Responses:**

```json
// 400 Bad Request - Invalid image
{
  "detail": "Front image quality too low. Sharpness score: 45 (minimum: 60)"
}

// 422 Unprocessable Entity - Validation error
{
  "detail": "Height must be between 100 and 250 cm"
}

// 413 Payload Too Large
{
  "detail": "Image file size exceeds 10MB limit"
}
```

**Processing Time:** 15-30 seconds (async recommended)

---

#### `GET /api/v1/scans/{scan_id}`

Retrieve a specific body scan by ID.

**Authentication:** Required (user must own the scan)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `scan_id` | UUID | Scan identifier |

**Example:**

```bash
curl -X GET "https://api.reddyfit.com/api/v1/scans/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

**Response (200 OK):**

Same structure as `POST /api/v1/scans` response above.

**Error Responses:**

```json
// 404 Not Found
{
  "detail": "Scan not found"
}

// 403 Forbidden
{
  "detail": "You don't have permission to access this scan"
}
```

---

#### `GET /api/v1/scans`

List all scans for the authenticated user.

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `user_id` | String | (from token) | Filter by user ID |
| `limit` | Integer | 10 | Number of results (1-100) |
| `offset` | Integer | 0 | Pagination offset |
| `sort` | String | `desc` | Sort order (`asc` or `desc`) |

**Example:**

```bash
curl -X GET "https://api.reddyfit.com/api/v1/scans?limit=20&offset=0&sort=desc" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

**Response (200 OK):**

```json
{
  "scans": [
    {
      "scan_id": "550e8400-e29b-41d4-a716-446655440000",
      "body_signature_id": "VTaper-BF14.5-A3F7C2-AI1.52",
      "timestamp": "2025-01-17T12:00:00Z",
      "aesthetic_score": 78.5,
      "body_type": "VTAPER"
    },
    {
      "scan_id": "660f9511-f30c-52e5-b827-557766551111",
      "body_signature_id": "Classic-BF16.2-B4G8D3-AI1.48",
      "timestamp": "2025-01-10T10:30:00Z",
      "aesthetic_score": 75.2,
      "body_type": "CLASSIC"
    }
  ],
  "total": 25,
  "limit": 20,
  "offset": 0
}
```

---

### Progress Tracking

#### `GET /api/v1/scans/{scan_id}/progress`

Compare a scan with previous scans to show progress.

**Authentication:** Required

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `scan_id` | UUID | Current scan to analyze |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lookback_weeks` | Integer | 4 | How far back to look for comparison |

**Example:**

```bash
curl -X GET "https://api.reddyfit.com/api/v1/scans/550e8400-e29b-41d4-a716-446655440000/progress?lookback_weeks=4" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

**Response (200 OK):**

```json
{
  "current_scan": {
    "scan_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-01-17T12:00:00Z",
    "body_fat_percent": 14.5,
    "aesthetic_score": 78.5
  },

  "previous_scan": {
    "scan_id": "660f9511-f30c-52e5-b827-557766551111",
    "timestamp": "2024-12-20T10:30:00Z",
    "body_fat_percent": 16.2,
    "aesthetic_score": 75.2
  },

  "changes": {
    "body_fat_percent_change": -1.7,
    "aesthetic_score_change": +3.3,
    "waist_change_cm": -2.5,
    "chest_change_cm": +1.2,
    "days_between_scans": 28
  },

  "insights": {
    "body_fat_trend": "decreasing",
    "muscle_mass_trend": "increasing",
    "estimated_weekly_progress": 0.43
  }
}
```

---

### Body Signature Search

#### `GET /api/v1/search/body-signature/{signature_id}`

Find similar body types across all users (anonymized).

**Authentication:** Required

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `signature_id` | String | Body signature to search for |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | Integer | 10 | Number of results (1-50) |

**Example:**

```bash
curl -X GET "https://api.reddyfit.com/api/v1/search/body-signature/VTaper-BF14.5-A3F7C2-AI1.52?limit=10" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

**Response (200 OK):**

```json
{
  "signature_id": "VTaper-BF14.5-A3F7C2-AI1.52",
  "similar_bodies": [
    {
      "similarity_score": 0.95,
      "body_type": "VTAPER",
      "body_fat_percent": 14.8,
      "adonis_index": 1.51,
      "timestamp": "2025-01-15T09:00:00Z"
    },
    {
      "similarity_score": 0.89,
      "body_type": "VTAPER",
      "body_fat_percent": 13.9,
      "adonis_index": 1.54,
      "timestamp": "2025-01-12T14:30:00Z"
    }
  ],
  "total_found": 47
}
```

**Note:** User IDs are NOT included for privacy.

---

### Recommendations

#### `GET /api/v1/scans/{scan_id}/recommendations`

Get personalized workout and nutrition recommendations for a scan.

**Authentication:** Required

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `scan_id` | UUID | Scan to generate recommendations for |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `goal` | String | `muscle_gain` | Fitness goal (`muscle_gain`, `fat_loss`, `maintenance`, `recomp`) |

**Example:**

```bash
curl -X GET "https://api.reddyfit.com/api/v1/scans/550e8400-e29b-41d4-a716-446655440000/recommendations?goal=muscle_gain" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

**Response (200 OK):**

```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "goal": "muscle_gain",

  "workout_plan": {
    "intensity": "moderate",
    "frequency": "4-5 days/week",
    "split": "Upper/Lower",
    "focus_areas": [
      "Chest (for upper body development)",
      "Shoulders (for V-taper enhancement)",
      "Back (for symmetry improvement)"
    ],
    "sample_workout": "Day 1: Upper (Chest, Shoulders, Triceps)\n- Bench Press: 4x8\n- Overhead Press: 3x10\n..."
  },

  "nutrition_plan": {
    "daily_calories": 2850,
    "macros": {
      "protein_g": 178,
      "carbs_g": 320,
      "fat_g": 95
    },
    "meal_split": "4 meals/day",
    "sample_day": "Meal 1 (Breakfast): Oatmeal with protein powder, banana\n..."
  },

  "key_focus_areas": [
    "Increase shoulder:waist ratio from 1.52 to 1.60",
    "Reduce body fat from 14.5% to 12%",
    "Maintain muscle symmetry during growth"
  ],

  "estimated_timeline_weeks": 12,

  "recovery_integration": {
    "whoop_recovery": 68.0,
    "recommended_intensity": "moderate",
    "rest_days": 2
  }
}
```

---

### User Management

#### `GET /api/v1/users/{user_id}/profile`

Get user profile and stats.

**Authentication:** Required (must be own user ID)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | String | Firebase user ID |

**Example:**

```bash
curl -X GET "https://api.reddyfit.com/api/v1/users/firebase_user_123/profile" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

**Response (200 OK):**

```json
{
  "user_id": "firebase_user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-06-15T10:00:00Z",
  "scan_count": 5,
  "latest_scan": {
    "scan_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-01-17T12:00:00Z",
    "aesthetic_score": 78.5
  }
}
```

---

#### `GET /api/v1/users/{user_id}/history`

Get full scan history for a user.

**Authentication:** Required

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | String | Firebase user ID |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | Integer | 10 | Number of scans |
| `offset` | Integer | 0 | Pagination offset |

**Example:**

```bash
curl -X GET "https://api.reddyfit.com/api/v1/users/firebase_user_123/history?limit=20" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

**Response (200 OK):**

```json
{
  "user_id": "firebase_user_123",
  "scans": [
    {
      "scan_id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2025-01-17T12:00:00Z",
      "body_fat_percent": 14.5,
      "aesthetic_score": 78.5,
      "body_type": "VTAPER"
    },
    {
      "scan_id": "660f9511-f30c-52e5-b827-557766551111",
      "timestamp": "2024-12-20T10:30:00Z",
      "body_fat_percent": 16.2,
      "aesthetic_score": 75.2,
      "body_type": "VTAPER"
    }
  ],
  "total": 5
}
```

---

### Metrics

#### `GET /api/v1/metrics`

Get API usage metrics (admin only).

**Authentication:** Required (admin role)

**Response (200 OK):**

```json
{
  "total_scans": 12450,
  "scans_last_24h": 125,
  "avg_processing_time_sec": 18.3,
  "cache_hit_rate": 0.67,
  "error_rate": 0.02,
  "active_users_last_7d": 450
}
```

---

## Webhooks (Future)

### Scan Complete Webhook

**POST to your endpoint when scan is complete**

```json
{
  "event": "scan.completed",
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "firebase_user_123",
  "timestamp": "2025-01-17T12:00:00Z",
  "body_signature_id": "VTaper-BF14.5-A3F7C2-AI1.52"
}
```

---

## SDKs

### Python SDK

```python
from reddyfit_client import ReddyFitClient

client = ReddyFitClient(
    api_key="YOUR_FIREBASE_TOKEN",
    base_url="https://api.reddyfit.com"
)

# Create scan
scan = client.scans.create(
    front_image="front.jpg",
    side_image="side.jpg",
    back_image="back.jpg",
    user_id="firebase_user_123",
    height_cm=178
)

print(f"Scan ID: {scan.scan_id}")
print(f"Body Type: {scan.aesthetic_score.body_type}")
```

### JavaScript SDK

```javascript
import { ReddyFitClient } from '@reddyfit/client';

const client = new ReddyFitClient({
  apiKey: 'YOUR_FIREBASE_TOKEN',
  baseUrl: 'https://api.reddyfit.com'
});

// Create scan
const scan = await client.scans.create({
  frontImage: frontFile,
  sideImage: sideFile,
  backImage: backFile,
  userId: 'firebase_user_123',
  heightCm: 178
});

console.log(`Scan ID: ${scan.scanId}`);
console.log(`Body Type: ${scan.aestheticScore.bodyType}`);
```

---

## Interactive Documentation

Visit **http://localhost:8000/docs** (local) or **https://api.reddyfit.com/docs** (production) for interactive Swagger UI documentation.

---

## Support

For API support:
- **GitHub Issues:** [github.com/DandaAkhilReddy/reddy/issues](https://github.com/DandaAkhilReddy/reddy/issues)
- **Email:** [Your Email]
- **Documentation:** [docs/](../../docs/)

---

**Last Updated:** 2025-01-17
**API Version:** v1
**Maintained by:** Akhil Reddy Danda
