# 🏋️ ReddyFit - AI-Powered Fitness Intelligence Platform

> Transform your fitness journey with AI-driven body analysis, personalized nutrition, and intelligent workout planning.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![GPT-4o](https://img.shields.io/badge/OpenAI-GPT--4o-412991.svg)](https://openai.com/)

## 🎯 Vision

ReddyFit is building the future of personalized fitness by combining cutting-edge AI, computer vision, and wearable data integration to deliver unprecedented insights into your body composition, health metrics, and fitness potential.

## ✨ Features

### 🔬 Photo Analysis (In Development - 25% Complete)
**20-Step Mathematical Body Scan Analysis System**

Transform 3 smartphone photos (front, side, back) into comprehensive body insights:
- 📸 **Multi-Angle AI Vision**: GPT-4o analyzes body composition from multiple perspectives
- 📊 **10+ Anthropometric Measurements**: Chest, waist, hip, limb circumferences via AI
- 📐 **Golden Ratio & Aesthetics**: Adonis Index, symmetry scoring, proportion analysis
- 🎯 **Body Type Classification**: V-Taper, Classic, Apple, Pear, Rectangular, Balanced
- 🔐 **Unique Body Signature**: Cryptographic fingerprint for each scan
- 🎨 **Aesthetic Scoring**: 0-100 score based on proportions, symmetry, composition

**Target**: 95%+ success rate (up from 37% baseline)
**Status**: Foundation complete, core pipeline in development
📖 [Read More](features/photoanalysis/README.md)

### ⌚ WHOOP Integration (Mock Data Ready)
**Wearable Data Intelligence**

- Real-time recovery & strain monitoring
- Sleep performance tracking
- HRV and resting heart rate analysis
- Personalized recommendations based on recovery status
- Mock dataset with 1,000 users × 30 days of realistic data

📖 [Read More](features/whoop-integration/README.md)

### 🍽️ Nutrition AI (Planned)
**AI-Powered Meal Planning**

- Personalized nutrition recommendations
- Meal plans adapted to recovery status (WHOOP integration)
- Macro optimization for body composition goals
- Food database with nutritional insights

📖 [Read More](features/nutrition-ai/README.md)

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
├── Photo Analysis Engine
│   ├── Image Validation (Step 1) ✅
│   ├── Preprocessing (Step 2)
│   ├── Angle Detection (Step 3)
│   ├── GPT-4o Vision Analysis (Steps 5-9)
│   ├── Mathematical Analysis (Steps 10-15)
│   └── Personalized Insights (Steps 16-20)
│
├── WHOOP Integration
│   ├── Mock Data API
│   ├── Production API Client
│   └── Recovery/Strain Analysis
│
├── Nutrition AI
│   └── GPT-4 Meal Planning
│
└── Workout AI
    └── GPT-4 Exercise Programming
```

## 📊 Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI | Async Python web framework |
| **AI/ML** | OpenAI GPT-4o | Vision & text intelligence |
| **Image Processing** | OpenCV, PIL, MediaPipe | Photo validation & pose detection |
| **Database** | Firebase Firestore | NoSQL document storage |
| **Storage** | Firebase Storage | Image hosting |
| **Wearables** | WHOOP API | Fitness tracker integration |
| **Validation** | Pydantic | Data validation & serialization |
| **Monitoring** | Sentry | Error tracking |

## 📈 Roadmap

### Phase 1: Foundation (Current - 25% Complete)
- [x] Project structure & configuration
- [x] Complete data models (Pydantic schemas)
- [x] WHOOP mock data integration
- [x] Image validation pipeline (Step 1)
- [ ] Image preprocessing (Step 2)
- [ ] Angle detection with MediaPipe (Step 3)

### Phase 2: Core AI Pipeline (Next)
- [ ] GPT-4o vision prompt engineering (Step 5)
- [ ] API retry logic & error handling (Step 6)
- [ ] Multi-strategy JSON extraction (Step 7)
- [ ] Schema validation & type checking (Step 8)
- [ ] Confidence scoring (Step 9)

### Phase 3: Mathematical Analysis
- [ ] Anthropometric measurements (Step 10)
- [ ] Golden Ratio & Adonis Index (Step 11)
- [ ] Symmetry coefficient (Step 12)
- [ ] Composition hash generation (Step 13)
- [ ] Body type classification (Step 14)
- [ ] Unique ID generation (Step 15)

### Phase 4: Integration & Intelligence
- [ ] Firestore persistence (Step 17)
- [ ] AI workout recommendations (Step 18)
- [ ] AI nutrition recommendations (Step 18)
- [ ] WHOOP-aware personalization (Step 18)

### Phase 5: Production
- [ ] Comprehensive error handling (Step 19)
- [ ] Performance optimization (<30s target) (Step 20)
- [ ] API endpoints & authentication
- [ ] Frontend dashboard
- [ ] Mobile app integration

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
