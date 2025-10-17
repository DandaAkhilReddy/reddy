"""
FastAPI Application - ReddyFit Photo Analysis API
Production-ready REST API for body composition analysis

Endpoints:
- POST /api/v1/scans - Upload photos and create scan
- GET /api/v1/scans/{scan_id} - Get scan results
- GET /api/v1/scans/user/{user_id} - Get user scan history
- POST /api/v1/recommendations/{scan_id} - Generate AI recommendations
- GET /api/v1/health - Health check endpoint
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time

# Import routes
from .routes import scan_routes, recommendation_routes, history_routes, health_routes

# Import middleware
from .middleware.auth import AuthMiddleware
from .middleware.rate_limiter import RateLimiterMiddleware

# Import error handler
from ..services.error_handler import get_error_handler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# LIFESPAN EVENTS
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("="*60)
    logger.info("ReddyFit Photo Analysis API Starting...")
    logger.info("="*60)

    # Initialize services
    error_handler = get_error_handler()
    logger.info("Error handler initialized")

    # Perform health checks
    health_status = await error_handler.health_check()
    logger.info(f"Health check status: {health_status['status']}")

    logger.info("API ready to accept requests")
    logger.info("="*60)

    yield

    # Shutdown
    logger.info("="*60)
    logger.info("Shutting down ReddyFit Photo Analysis API...")
    logger.info("="*60)


# ============================================================
# APPLICATION SETUP
# ============================================================

app = FastAPI(
    title="ReddyFit Photo Analysis API",
    description="""
    AI-Powered Body Composition Analysis API

    Transform 3 smartphone photos into comprehensive body insights:
    - 📸 Multi-angle AI vision analysis
    - 📊 10+ anthropometric measurements
    - 📐 Golden ratio & aesthetic scoring
    - 🎯 Body type classification
    - 🤖 AI-powered workout & nutrition recommendations
    - 💾 Scan history & progress tracking

    Built with Claude 3.5 Sonnet, FastAPI, and Firebase.
    """,
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# ============================================================
# MIDDLEWARE
# ============================================================

# CORS - Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev
        "http://localhost:3001",  # Next.js dev
        "https://reddyfit.com",   # Production (update with your domain)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Authentication middleware (applied to all routes except /health)
app.add_middleware(AuthMiddleware, exclude_paths=["/api/health", "/api/docs", "/api/redoc", "/api/openapi.json"])

# Rate limiting middleware
app.add_middleware(RateLimiterMiddleware, requests_per_minute=60)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 3))
    return response


# ============================================================
# EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    error_handler = get_error_handler()

    # Log error
    await error_handler.log_error(
        error=exc,
        step="API Request",
        context={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else None
        },
        severity="error"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Our team has been notified.",
            "request_id": str(time.time())
        }
    )


# ============================================================
# ROUTES
# ============================================================

# Include routers
app.include_router(
    scan_routes.router,
    prefix="/api/v1",
    tags=["Scans"]
)

app.include_router(
    recommendation_routes.router,
    prefix="/api/v1",
    tags=["Recommendations"]
)

app.include_router(
    history_routes.router,
    prefix="/api/v1",
    tags=["History"]
)

app.include_router(
    health_routes.router,
    prefix="/api",
    tags=["Health"]
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - API info"""
    return {
        "name": "ReddyFit Photo Analysis API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/api/docs",
        "health": "/api/health",
        "endpoints": {
            "scans": "/api/v1/scans",
            "recommendations": "/api/v1/recommendations",
            "history": "/api/v1/history"
        }
    }


@app.get("/api", include_in_schema=False)
async def api_info():
    """API version info"""
    return {
        "api_version": "v1",
        "features": {
            "photo_analysis": "enabled",
            "ai_recommendations": "enabled",
            "scan_history": "enabled",
            "progress_tracking": "enabled"
        },
        "documentation": "/api/docs"
    }


# ============================================================
# DEVELOPMENT SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
