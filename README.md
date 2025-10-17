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

### 🔬 Photo Analysis (In Development - 70% Complete)
**20-Step Mathematical Body Scan Analysis System**

Transform 3 smartphone photos (front, side, back) into comprehensive body insights:
- 📸 **Multi-Angle AI Vision**: Claude 3.5 Sonnet analyzes body composition from multiple perspectives
- 📊 **10+ Anthropometric Measurements**: Chest, waist, hip, limb circumferences via AI
- 📐 **Golden Ratio & Aesthetics**: Adonis Index, symmetry scoring, proportion analysis
- 🎯 **Body Type Classification**: V-Taper, Classic, Apple, Pear, Rectangular, Balanced
- 🔐 **Unique Body Signature**: Cryptographic fingerprint for each scan
- 🎨 **Aesthetic Scoring**: 0-100 score based on proportions, symmetry, composition

**Target**: 95%+ success rate (up from 37% baseline)
**Status**: Steps 1-9 complete (Claude API migration complete), tested
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
- OpenAI API key (GPT-4o access)
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
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o

# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-bucket
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Optional: WHOOP API (uses mock data by default)
WHOOP_CLIENT_ID=your-client-id
WHOOP_CLIENT_SECRET=your-secret
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
│   ├── Mathematical Analysis (Steps 10-15) 🚧
│   └── Personalized Insights (Steps 16-20) 🚧
│
├── Nutrition Agent System (OpenAI GPT-4 + LangChain)
│   ├── Macro Calculator Agent ✅
│   ├── Meal Planner Agent ✅
│   ├── Recipe Suggester Agent ✅
│   ├── LangGraph Workflow Orchestration ✅
│   ├── Body Composition Integration (Photo Analysis) ✅
│   └── WHOOP Recovery Integration ✅
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

### Phase 3: Mathematical Analysis (Next - 0% Complete)
- [ ] Anthropometric measurements (Step 10)
- [ ] Golden Ratio & Adonis Index (Step 11)
- [ ] Symmetry coefficient (Step 12)
- [ ] Composition hash generation (Step 13)
- [ ] Body type classification (Step 14)
- [ ] Unique ID generation (Step 15)

### Phase 4: Integration & Intelligence (Upcoming)
- [ ] Firestore persistence (Step 17)
- [ ] AI workout recommendations (Step 18)
- [ ] WHOOP-aware personalization (Step 18)
- [ ] Nutrition API integrations (Nutritionix, USDA)
- [ ] Real food & recipe database

### Phase 5: Production (Future)
- [ ] Comprehensive error handling (Step 19)
- [ ] Performance optimization (<30s target) (Step 20)
- [ ] FastAPI REST endpoints
- [ ] Authentication & authorization
- [ ] Frontend dashboard
- [ ] Mobile app integration
- [ ] Meal tracking & logging
- [ ] Grocery list generation

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

- OpenAI for GPT-4o vision capabilities
- MediaPipe for pose detection
- WHOOP for fitness wearable inspiration
- Open-source community for amazing tools

## 📞 Support

- 📧 Email: [Your Email]
- 💬 Issues: [GitHub Issues](https://github.com/DandaAkhilReddy/reddy/issues)
- 📖 Documentation: [docs/](docs/)

---

**⭐ Star this repo if you find it helpful!**

*Built with ❤️ by Akhil Reddy Danda*
