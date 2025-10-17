# ReddyFit Photo Analysis REST API

**Version**: 2.0.0
**Status**: ✅ Production Ready

Complete REST API for AI-powered body composition analysis.

---

## 🚀 Quick Start

### Installation

```bash
cd features/photoanalysis
pip install -r requirements.txt
```

### Start API Server

```bash
# Development mode
python -m api.main

# Production mode (with uvicorn)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server runs on: `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

---

## 📋 API Endpoints

### Scans

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/scans` | Upload 3 photos and create scan |
| GET | `/api/v1/scans/{scan_id}` | Get scan results |

### Recommendations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/recommendations/{scan_id}` | Generate AI recommendations |
| GET | `/api/v1/recommendations/{scan_id}` | Get cached recommendations |

### History

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/history/user/{user_id}` | Get user scan history |
| GET | `/api/v1/history/user/{user_id}/progress` | Get progress comparison |
| GET | `/api/v1/history/user/{user_id}/latest` | Get latest scan |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Basic health check |
| GET | `/api/health/detailed` | Detailed health with metrics |
| GET | `/api/health/ready` | Kubernetes readiness probe |
| GET | `/api/health/live` | Kubernetes liveness probe |

---

## 🔐 Authentication

### Firebase JWT Tokens

All endpoints (except `/health` and `/docs`) require Firebase authentication.

**Header:**
```
Authorization: Bearer <firebase_jwt_token>
```

**Mock Mode** (for testing):
If Firebase SDK is not configured, the API accepts mock tokens:
```
Authorization: Bearer mock_user_test123
```

### Get Firebase Token (JavaScript)

```javascript
import { getAuth } from "firebase/auth";

const auth = getAuth();
const user = auth.currentUser;
const token = await user.getIdToken();

// Use token in API requests
fetch("http://localhost:8000/api/v1/scans", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
});
```

---

## 📖 Example Usage

### 1. Create Scan (Upload Photos)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/scans" \
  -H "Authorization: Bearer <token>" \
  -F "front_image=@front.jpg" \
  -F "side_image=@side.jpg" \
  -F "back_image=@back.jpg" \
  -F "user_id=user_abc123" \
  -F "height_cm=178" \
  -F "gender=male" \
  -F "fitness_goal=muscle_gain"
```

**Response:**
```json
{
  "scan_id": "scan_a1b2c3d4e5f6",
  "status": "completed",
  "message": "Scan created successfully",
  "estimated_processing_time_sec": 25.0
}
```

### 2. Generate Recommendations

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/recommendations/scan_a1b2c3d4e5f6" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_id": "scan_a1b2c3d4e5f6",
    "fitness_goal": "muscle_gain",
    "dietary_restrictions": ["gluten_free"],
    "meals_per_day": 4
  }'
```

**Response:**
```json
{
  "scan_id": "scan_a1b2c3d4e5f6",
  "workout_plan": "4-day Upper/Lower split...",
  "nutrition_plan": "Daily macros: 2400 cal, 180g protein...",
  "recovery_advice": "WHOOP recovery: 85% - High intensity OK",
  "key_focus_areas": [
    "Build wider shoulders",
    "Maintain low body fat"
  ],
  "estimated_timeline_weeks": 28,
  "generated_at": "2025-10-17T10:35:00Z"
}
```

### 3. Get Scan History

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/history/user/user_abc123?limit=10" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "user_id": "user_abc123",
  "total_scans": 15,
  "scans": [
    {
      "scan_id": "scan_latest",
      "body_signature_id": "VTaper-BF12.5-A3F7C2-AI1.56",
      "timestamp": "2025-10-17T10:30:00Z",
      "body_type": "V-Taper",
      "body_fat_percent": 12.5,
      "overall_score": 85.0,
      "confidence": 0.92
    }
  ],
  "has_more": true
}
```

### 4. Get Progress Comparison

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/history/user/user_abc123/progress?weeks_back=4" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "user_id": "user_abc123",
  "time_between_scans_days": 28,
  "changes": {
    "body_fat_change_percent": -1.5,
    "aesthetic_score_change": 3.5,
    "adonis_index_change": 0.08
  },
  "body_type_changed": false,
  "progress_summary": [
    "Lost 1.5% body fat - Excellent!",
    "Aesthetic score improved by 3.5 points"
  ]
}
```

### 5. Health Check

**Request:**
```bash
curl -X GET "http://localhost:8000/api/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-17T10:30:00Z",
  "checks": {
    "ai_api": {"status": "up", "message": "OK"},
    "firestore": {"status": "up", "message": "OK"},
    "sentry": {"status": "up"}
  },
  "error_statistics": {}
}
```

---

## ⚡ Rate Limiting

**Default Limits:**
- 60 requests per minute per IP

**Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 60
```

**Rate Limit Exceeded (429):**
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Max 60 requests per minute.",
  "retry_after": 30
}
```

---

## 📊 Response Headers

All responses include:
- `X-Process-Time`: Request processing time (seconds)
- `X-RateLimit-Limit`: Max requests per window
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time until reset (seconds)

---

## ❌ Error Handling

### Standard Error Format

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": ["Additional error details"],
  "request_id": "req_1234567890"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (processing) |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (missing/invalid token) |
| 404 | Not Found |
| 422 | Unprocessable Entity (validation error) |
| 429 | Too Many Requests (rate limit) |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## 🔧 Configuration

### Environment Variables

```env
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Anthropic Claude (for photo analysis)
ANTHROPIC_API_KEY=sk-ant-api03-...

# OpenAI (for nutrition agent)
OPENAI_API_KEY=sk-...

# Optional: Sentry
SENTRY_DSN=https://...

# Optional: Redis (for distributed rate limiting)
REDIS_URL=redis://localhost:6379
```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./firebase-credentials.json:/app/firebase-credentials.json
```

---

## ☸️ Kubernetes Deployment

### Deployment YAML

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
      - name: api
        image: reddyfit/photo-analysis-api:2.0.0
        ports:
        - containerPort: 8000
        env:
        - name: FIREBASE_PROJECT_ID
          valueFrom:
            secretKeyRef:
              name: reddyfit-secrets
              key: firebase-project-id
        livenessProbe:
          httpGet:
            path: /api/health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## 📈 Performance

### Benchmarks

- **Scan Creation**: ~25s (includes AI processing)
- **Recommendations**: ~2s (with caching: <100ms)
- **History Retrieval**: ~200ms
- **Health Check**: ~50ms

### Optimization Features

- Multi-tier caching (memory + Redis)
- GZip compression
- Async/await throughout
- Connection pooling
- Request profiling

---

## 🧪 Testing

### Run Tests

```bash
pytest api/tests/
```

### Manual Testing

Use the interactive Swagger UI:
```
http://localhost:8000/api/docs
```

---

## 📞 Support

- **Documentation**: http://localhost:8000/api/docs
- **GitHub Issues**: https://github.com/DandaAkhilReddy/reddy/issues
- **Email**: support@reddyfit.com

---

## 📄 License

MIT License - see [LICENSE](../../../LICENSE)
