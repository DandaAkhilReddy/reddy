# ReddyFit Photo Analysis API

> AI-Powered Body Composition Analysis from Smartphone Photos

[![Live API](https://img.shields.io/badge/API-Live-success)](https://reddyfit-api.fly.dev)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)](https://fastapi.tiangolo.com/)
[![Claude AI](https://img.shields.io/badge/Claude-3.5%20Sonnet-5A67D8)](https://www.anthropic.com/)

Transform 3 smartphone photos into comprehensive body composition insights powered by Claude 3.5 Sonnet vision AI.

## Live API

**Production URL:** https://reddyfit-api.fly.dev

**Health Check:** https://reddyfit-api.fly.dev/api/health

**API Documentation:** https://reddyfit-api.fly.dev/api/docs

---

## Features

### Core Capabilities
- **Multi-Angle AI Vision Analysis** - Upload front, side, and back photos
- **10+ Anthropometric Measurements** - Chest, waist, hips, biceps, thighs, shoulders, and more
- **Body Composition Estimation** - Body fat percentage and muscle definition
- **Golden Ratio Scoring** - Adonis Index and aesthetic proportions
- **Body Type Classification** - V-Taper, Classic, Rectangular, Apple, Pear, Balanced
- **Symmetry Analysis** - Multi-factor symmetry scoring
- **AI-Powered Recommendations** - Personalized workout and nutrition plans
- **Scan History & Progress Tracking** - Store and compare multiple scans
- **Confidence Scoring** - Multi-factor confidence metrics for reliability

### Technical Highlights
- **Claude 3.5 Sonnet Vision AI** - State-of-the-art multimodal AI
- **MediaPipe Pose Detection** - Accurate angle detection and validation
- **Firebase Firestore** - Real-time database for scan storage
- **FastAPI Framework** - High-performance async API
- **Docker Containerization** - Consistent deployment across environments
- **Fly.io Cloud Hosting** - Global edge deployment

---

## Quick Start

### Prerequisites
- Python 3.11+
- Anthropic API key (Claude)
- Firebase project with Firestore
- Docker (for containerized deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/DandaAkhilReddy/reddy.git
cd reddy/features/photoanalysis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Create a `.env` file with the following variables:

```env
# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_key_here

# Firebase
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_bucket.appspot.com
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json

# Application
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=7000
DEBUG=True
```

### Run Locally

```bash
# Start the API server
uvicorn photoanalysis.api.main:app --host 0.0.0.0 --port 7000 --reload

# API will be available at:
# http://localhost:7000/api/docs
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t reddyfit-api .

# Run the container
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key \
  -e FIREBASE_PROJECT_ID=your_project \
  reddyfit-api
```

---

## API Usage Example

### Create a Body Scan

```bash
curl -X POST "https://reddyfit-api.fly.dev/api/v1/scans" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "front_image=@front.jpg" \
  -F "side_image=@side.jpg" \
  -F "back_image=@back.jpg" \
  -F "user_id=user123" \
  -F "height_cm=175" \
  -F "weight_kg=75"
```

### Get Scan Results

```bash
curl "https://reddyfit-api.fly.dev/api/v1/scans/{scan_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Generate AI Recommendations

```bash
curl -X POST "https://reddyfit-api.fly.dev/api/v1/recommendations/{scan_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Technology Stack

### Backend
- **Framework:** FastAPI 0.109.0
- **Language:** Python 3.11
- **Server:** Uvicorn (ASGI)

### AI & Machine Learning
- **Vision AI:** Anthropic Claude 3.5 Sonnet
- **Pose Detection:** MediaPipe 0.10.9
- **Image Processing:** OpenCV 4.9.0, Pillow 10.2.0
- **Numerical Computing:** NumPy 1.26.3

### Database & Storage
- **Database:** Firebase Firestore
- **Storage:** Firebase Cloud Storage
- **Authentication:** Firebase Admin SDK

### Deployment
- **Platform:** Fly.io
- **Containerization:** Docker
- **Base Image:** Python 3.11-slim
- **Region:** iad (Virginia, USA)

---

## Project Structure

```
photoanalysis/
├── api/                    # FastAPI application
│   ├── main.py            # Application entry point
│   ├── routes/            # API route handlers
│   ├── middleware/        # Auth, rate limiting
│   └── models.py          # Request/response models
├── services/              # Business logic
│   ├── vision_pipeline.py     # Main analysis orchestrator
│   ├── claude_vision_client.py # Claude API integration
│   ├── confidence_scorer.py   # Multi-factor scoring
│   ├── body_type_classifier.py # Body type detection
│   ├── ratio_calculator.py    # Golden ratio calculations
│   └── recommendation_engine.py # AI recommendations
├── models/                # Data models
│   └── schemas.py         # Pydantic schemas
├── utils/                 # Utilities
│   ├── image_validator.py # Image quality checks
│   ├── image_processor.py # Image preprocessing
│   └── angle_detector.py  # Pose angle detection
├── config/                # Configuration
│   └── settings.py        # Environment settings
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
└── docs/                  # Documentation
```

---

## Documentation

- **[Architecture](./ARCHITECTURE.md)** - System design and component architecture
- **[Technical Specifications](./TECHNICAL_SPECIFICATIONS.md)** - Detailed technical documentation
- **[API Documentation](./API_DOCUMENTATION.md)** - Complete API reference
- **[Tools & Dependencies](./TOOLS_AND_DEPENDENCIES.md)** - Technology stack details
- **[Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions
- **[Changelog](./CHANGELOG.md)** - Version history and updates

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=photoanalysis --cov-report=html

# Run specific test file
pytest tests/test_vision_pipeline.py
```

### Code Quality

```bash
# Format code with black
black photoanalysis/

# Lint with flake8
flake8 photoanalysis/

# Type checking with mypy
mypy photoanalysis/
```

---

## Performance

### Response Times
- Image validation: < 1s
- AI vision analysis: 15-30s (depends on Claude API)
- Complete scan pipeline: 20-35s
- Health check: < 100ms

### Scalability
- Async processing with FastAPI
- Horizontal scaling on Fly.io
- Rate limiting: 10 requests/minute per user
- Image size limits: 10MB per image

---

## Security

- JWT-based authentication
- API key validation
- Rate limiting per user/IP
- Input validation with Pydantic
- Secure environment variable management
- HTTPS-only in production

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is proprietary software. All rights reserved.

---

## Contact

**Developer:** Akhil Reddy Danda
**Email:** akhilreddydanda3@gmail.com
**GitHub:** [@DandaAkhilReddy](https://github.com/DandaAkhilReddy)
**Repository:** https://github.com/DandaAkhilReddy/reddy

---

## Acknowledgments

- **Anthropic** - Claude 3.5 Sonnet vision AI
- **Google** - MediaPipe pose detection and Firebase
- **FastAPI** - Modern Python web framework
- **Fly.io** - Cloud hosting platform

---

**Built with ❤️ by Akhil Reddy**
