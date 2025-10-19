# ReddyFit Photo Analysis API - System Architecture

Complete architecture documentation for the body composition analysis system.

## System Overview

Cloud-native API leveraging Claude 3.5 Sonnet for AI-powered body analysis from smartphone photos.

**Last Updated:** 2025-10-19  
**Version:** 2.0.0

## Components
- API Layer: FastAPI + middleware
- Vision Pipeline: 20-step orchestration
- AI Integration: Claude + MediaPipe
- Data Layer: Firebase

## Deployment
- Platform: Fly.io
- Container: Docker (Python 3.11-slim)
- Region: iad (Virginia, USA)
