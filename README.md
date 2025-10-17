# 🏋️ ReddyFit - AI-Powered Fitness Intelligence Platform

> Transform your fitness journey with AI-driven body analysis, personalized nutrition, and intelligent workout planning.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![Claude 3.5](https://img.shields.io/badge/Anthropic-Claude%203.5-5A67D8.svg)](https://anthropic.com/)
[![GPT-4](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)](https://openai.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.7-2C3E50.svg)](https://langchain.com/)
[![CodeRabbit](https://img.shields.io/badge/CodeRabbit-Enabled-brightgreen)](https://coderabbit.ai)

## 🎯 Vision

ReddyFit is building the future of personalized fitness by combining cutting-edge AI, computer vision, and wearable data integration to deliver unprecedented insights into your body composition, health metrics, and fitness potential.

## ✨ Features

### 🔬 Photo Analysis (Production Ready - 100% Complete!)
**20-Step Mathematical Body Scan Analysis System**

Transform 3 smartphone photos (front, side, back) into comprehensive body insights:
- 📸 **Multi-Angle AI Vision**: Claude 3.5 Sonnet analyzes body composition from multiple perspectives
- 📊 **10+ Anthropometric Measurements**: Chest, waist, hip, limb circumferences via AI
- 📐 **Golden Ratio & Aesthetics**: Adonis Index, symmetry scoring, proportion analysis
- 🎯 **Body Type Classification**: V-Taper, Classic, Apple, Pear, Rectangular, Balanced
- 🔐 **Unique Body Signature**: Cryptographic fingerprint for each scan
- 🎨 **Aesthetic Scoring**: 0-100 score based on proportions, symmetry, composition
- 💾 **Firestore Persistence**: Atomic transactions, scan history, progress tracking
- 🤖 **AI Recommendations**: Personalized workout & nutrition plans
- 🛡️ **Error Handling**: Retry logic, Sentry monitoring, graceful fallbacks
- ⚡ **Performance**: Multi-tier caching, parallel processing, <30s target

**Target**: 95%+ success rate (up from 37% baseline)
**Status**: All 20 steps complete! Ready for production deployment ✅
📖 [Read More](features/photoanalysis/README.md)

### ⌚ WHOOP Integration (Mock Data Ready)
**Wearable Data Intelligence**

- Real-time recovery & strain monitoring
- Sleep performance tracking
- HRV and resting heart rate analysis
- Personalized recommendations based on recovery status
- Mock dataset with 1,000 users × 30 days of realistic data

📖 [Read More](features/whoop-integration/README.md)

### 🍽️ Nutrition Agent (Complete - Production Ready)
**AI-Powered Meal Planning System**

Multi-agent AI system built with LangChain, LangGraph, and OpenAI GPT-4:
- 🎯 **Smart Macro Calculation**: BMR/TDEE with body composition integration (from photo analysis)
- ⌚ **Recovery-Aware**: Adjusts calories based on WHOOP recovery score (green/yellow/red zones)
- 🍱 **Intelligent Meal Planning**: Splits macros across 3-6 meals with dietary restriction support
- 📖 **Recipe Suggestions**: Matches recipes to meal requirements with accuracy scoring
- 🔄 **LangGraph Workflow**: Orchestrates 3 agents sequentially with error handling
- 🌱 **Dietary Support**: Vegan, vegetarian, keto, paleo, gluten-free, etc.

**Status**: ✅ Foundation complete with mock data, ready for production API integration
📖 [Read More](features/nutrition-agent/README.md)

### 🚀 REST API (Production Ready - Complete!)
**FastAPI Backend with Full Authentication**

Production-ready REST API with 11 endpoints:
- 🔐 **Firebase JWT Authentication**: Secure token-based auth with expiration handling
- 📸 **Scan Management**: Create, retrieve, list scans with pagination
- 👤 **User Management**: Profile and scan history endpoints
- 🔍 **Body Signature Search**: Find similar body types across all users
- 📊 **Progress Tracking**: Compare scans over time (4-week lookback)
- 🚦 **Rate Limiting**: Token bucket algorithm (per-user + per-IP protection)
- 🏥 **Health Checks**: Readiness and liveness probes for Kubernetes
- 📈 **Metrics**: Performance monitoring and error tracking

**Status**: ✅ All endpoints implemented with auth, validation, and error handling
📖 [Read More](api/README.md)

### 💪 Workout AI (Planned)
**Intelligent Exercise Programming**

- Custom workout plans based on body type & goals
- Exercise selection optimized for symmetry improvement
- Progressive overload tracking
- Recovery-aware programming

📖 [Read More](features/workout-ai/README.md)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Anthropic API key (Claude 3.5 Sonnet access for photo analysis)
- OpenAI API key (GPT-4 for nutrition agent - optional)
- Firebase project (for storage & database)

### Installation

```bash
# Clone the repository
git clone https://github.com/DandaAkhilReddy/reddy.git
cd reddy

# Install photo analysis feature
cd features/photoanalysis
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` file in `features/photoanalysis/`:

```env
# Anthropic Configuration (Claude 3.5 Sonnet for photo analysis)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# OpenAI Configuration (GPT-4 for nutrition agent - optional)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo

# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-bucket
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Optional: WHOOP API (uses mock data by default)
WHOOP_CLIENT_ID=your-client-id
WHOOP_CLIENT_SECRET=your-secret

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379
```

### Run Photo Analysis

```python
from features.photoanalysis.utils.image_validator import validate_image

# Validate image quality
with open("front_photo.jpg", "rb") as f:
    quality = validate_image(f.read(), "front_photo.jpg")

print(f"Valid: {quality.is_valid}")
print(f"Quality Score: {quality.quality_score}/100")
print(f"Sharpness: {quality.sharpness_score}")
```

### Test WHOOP Mock Data

```python
from features.whoop_integration.mock_data import get_mock_whoop_data

data = get_mock_whoop_data("user_123", profile_type="athlete_high_recovery")
print(f"Recovery: {data['recovery_score']}")
print(f"Strain: {data['strain_score']}")
print(f"Sleep: {data['sleep_hours']}h")
```

### Run REST API Server

```bash
cd features/photoanalysis
python -m api.main

# Server starts at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Create a body scan via API:**

```bash
curl -X POST "http://localhost:8000/api/v1/scans" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -F "front_image=@front.jpg" \
  -F "side_image=@side.jpg" \
  -F "back_image=@back.jpg" \
  -F "user_id=user_123" \
  -F "height_cm=178" \
  -F "gender=male"
```

**Get scan result:**

```bash
curl -X GET "http://localhost:8000/api/v1/scans/{scan_id}" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

## 🏗️ Architecture

```
ReddyFit Platform
│
├── Photo Analysis Engine (Claude 3.5 Sonnet)
│   ├── Image Validation (Step 1) ✅
│   ├── Preprocessing (Step 2) ✅
│   ├── Angle Detection (Step 3) ✅
│   ├── Claude Vision Analysis (Steps 4-6) ✅
│   ├── JSON Extraction (Step 7) ✅
│   ├── Schema Validation (Step 8) ✅
│   ├── Confidence Scoring (Step 9) ✅
│   ├── Anthropometric Measurements (Step 10) ✅
│   ├── Golden Ratio & Body Ratios (Step 11) ✅
│   ├── Symmetry Analysis (Step 12) ✅
│   ├── Composition Hash (Step 13) ✅
│   ├── Body Type Classification (Step 14) ✅
│   ├── Unique ID Generation (Step 15) ✅
│   ├── Scan Assembly (Step 16) ✅
│   ├── Firestore Persistence (Step 17) ✅
│   ├── AI Recommendations (Step 18) ✅
│   ├── Error Handling & Monitoring (Step 19) ✅
│   └── Performance Optimization (Step 20) ✅
│
├── Nutrition Agent System (OpenAI GPT-4 + LangChain)
│   ├── Macro Calculator Agent ✅
│   ├── Meal Planner Agent ✅
│   ├── Recipe Suggester Agent ✅
│   ├── LangGraph Workflow Orchestration ✅
│   ├── Body Composition Integration (Photo Analysis) ✅
│   └── WHOOP Recovery Integration ✅
│
├── REST API (FastAPI)
│   ├── Scan Routes (create, get, list, progress) ✅
│   ├── User Routes (profile, history) ✅
│   ├── Search Routes (body signature lookup) ✅
│   ├── Health Routes (readiness, liveness, metrics) ✅
│   ├── Firebase JWT Authentication ✅
│   ├── Token Bucket Rate Limiting ✅
│   └── CORS & Error Middleware ✅
│
├── WHOOP Integration
│   ├── Mock Data API ✅
│   ├── Production API Client 🚧
│   └── Recovery/Strain Analysis ✅
│
└── Workout AI (Planned)
    └── GPT-4 Exercise Programming
```

## 📊 Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI | Async Python web framework |
| **AI - Vision** | Anthropic Claude 3.5 Sonnet | Photo analysis & body composition |
| **AI - Agents** | OpenAI GPT-4-turbo | Nutrition planning & meal generation |
| **Agent Framework** | LangChain + LangGraph | Multi-agent orchestration |
| **Image Processing** | OpenCV, PIL, MediaPipe | Photo validation & pose detection |
| **Database** | Firebase Firestore | NoSQL document storage |
| **Storage** | Firebase Storage | Image hosting |
| **Wearables** | WHOOP API | Fitness tracker integration |
| **Validation** | Pydantic | Data validation & serialization |
| **Monitoring** | Sentry | Error tracking |

## 📈 Roadmap

### Phase 1: Foundation ✅ (Complete - 100%)
- [x] Project structure & configuration
- [x] Complete data models (Pydantic schemas)
- [x] WHOOP mock data integration
- [x] Image validation pipeline (Step 1)
- [x] Image preprocessing (Step 2)
- [x] Angle detection with MediaPipe (Step 3)

### Phase 2: Core AI Pipeline ✅ (Complete - 100%)
- [x] Claude 3.5 vision prompt engineering (Step 5)
- [x] API retry logic & error handling (Step 6)
- [x] Multi-strategy JSON extraction (Step 7)
- [x] Schema validation & type checking (Step 8)
- [x] Confidence scoring (Step 9)
- [x] Comprehensive test suite
- [x] Migration from OpenAI to Anthropic Claude

### Phase 2.5: Nutrition Agent System ✅ (Complete - 100%)
- [x] Macro Calculator Agent (BMR/TDEE with recovery adjustment)
- [x] Meal Planner Agent (splits macros across meals)
- [x] Recipe Suggester Agent (matches recipes to requirements)
- [x] LangGraph workflow orchestration
- [x] Body composition integration (photo analysis)
- [x] WHOOP recovery integration
- [x] Comprehensive documentation
- [x] End-to-end test suite

### Phase 3: Mathematical Analysis ✅ (Complete - 100%)
- [x] Anthropometric measurements calculator (Step 10)
- [x] Golden Ratio & Adonis Index calculator (Step 11)
- [x] Symmetry coefficient analyzer (Step 12)
- [x] Composition hash generator (Step 13)
- [x] Body type classifier with aesthetic scoring (Step 14)
- [x] Unique body signature ID generator (Step 15)
- [x] Scan result assembler orchestration (Step 16)
- [x] Comprehensive testing (5/5 tests passing)

### Phase 4: Integration & Intelligence ✅ (Complete - 100%)
- [x] Firestore persistence client (Step 17)
- [x] AI recommendation engine (Step 18)
- [x] Workout recommendations (body type + symmetry aware)
- [x] Nutrition recommendations (integrated with nutrition-agent)
- [x] WHOOP recovery-aware personalization
- [x] Comprehensive error handling & monitoring (Step 19)
- [x] Performance optimization with caching & parallelization (Step 20)
- [x] Integration tests (4/4 services implemented)

### Phase 5: REST API & Authentication ✅ (Complete - 100%)
- [x] FastAPI REST API with 11 production endpoints
- [x] Firebase JWT authentication middleware
- [x] Token bucket rate limiting (per-user + per-IP)
- [x] Multipart file upload handling (3 photos)
- [x] Health check and metrics endpoints
- [x] CORS configuration for web clients
- [x] Error response standardization
- [x] API versioning (/api/v1)

### Phase 6: Vision Pipeline Integration ✅ (Complete - 100%)
- [x] Complete Steps 1-9 orchestration workflow
- [x] User profile validator (Step 4) with WHOOP integration
- [x] Claude 3.5 Sonnet vision API integration
- [x] Async/await throughout for optimal performance
- [x] Error propagation and handling
- [x] Performance profiling integration
- [x] End-to-end photo upload to scan result flow
- [x] Integration tests for vision pipeline

### Phase 7: Production Deployment (Next Priority)
- [ ] Cloud deployment (Firebase + Cloud Run / AWS Lambda)
- [ ] CI/CD pipeline setup (GitHub Actions)
- [ ] Production environment configuration
- [ ] Database migrations and seeding
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Performance benchmarking
- [ ] Security hardening and penetration testing

### Phase 8: Frontend & Mobile (Future)
- [ ] React/Next.js dashboard
- [ ] Mobile app (React Native / Flutter)
- [ ] Real-time progress tracking UI
- [ ] Meal tracking & logging interface
- [ ] Grocery list generation
- [ ] Social features (compare with friends)
- [ ] Progress photo timeline

## 🎯 Success Metrics

| Metric | Baseline | Current | Target |
|--------|----------|---------|--------|
| **Scan Success Rate** | 37% | 🚧 TBD | ≥95% |
| **JSON Extraction** | 95% | 🚧 TBD | 99%+ |
| **Processing Time** | ~45s | 🚧 TBD | <30s |
| **Data Completeness** | 80% | 🚧 TBD | 98% |
| **User Profile Errors** | 5% | 🚧 TBD | 0% |

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment.md)
- [Photo Analysis Deep Dive](docs/photoanalysis/20-step-plan.md)
- [WHOOP Integration Guide](docs/whoop/mock-data-guide.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone the repo
git clone https://github.com/YOUR_USERNAME/reddy.git
cd reddy

# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes and test
pytest tests/

# Commit with conventional commits
git commit -m "feat(photoanalysis): add image rotation correction"

# Push and create a Pull Request
git push origin feature/amazing-feature
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Akhil Reddy Danda**

- GitHub: [@DandaAkhilReddy](https://github.com/DandaAkhilReddy)
- WHOOP Mock Dataset: [whoopmockdataset](https://github.com/DandaAkhilReddy/whoopmockdataset)

## 🙏 Acknowledgments

- Anthropic for Claude 3.5 Sonnet vision capabilities
- OpenAI for GPT-4 nutrition agent capabilities
- MediaPipe for pose detection
- WHOOP for fitness wearable inspiration
- FastAPI for the amazing async web framework
- LangChain & LangGraph for multi-agent orchestration
- Open-source community for amazing tools

## 📞 Support

- 📧 Email: [Your Email]
- 💬 Issues: [GitHub Issues](https://github.com/DandaAkhilReddy/reddy/issues)
- 📖 Documentation: [docs/](docs/)

---

**⭐ Star this repo if you find it helpful!**

*Built with ❤️ by Akhil Reddy Danda*
