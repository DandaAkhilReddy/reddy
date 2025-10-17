"""
Health Check Routes - Service health and monitoring endpoints
"""
import logging
from fastapi import APIRouter
from datetime import datetime

from ..models import HealthCheckResponse
from ...services.error_handler import get_error_handler
from ...services.performance_optimizer import get_performance_optimizer

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# GET /api/health - Basic health check
# ============================================================

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="""
    Check API health and service status.

    **Returns:**
    - Overall status (healthy/degraded)
    - Individual service checks (AI API, Firestore, Sentry)
    - Error statistics
    - Timestamp

    **Use Case**: Load balancers, monitoring tools, uptime checks
    """,
    tags=["Health"]
)
async def health_check():
    """
    Basic health check endpoint

    Returns current health status of all services
    """

    error_handler = get_error_handler()

    try:
        # Perform health check
        health_status = await error_handler.health_check()

        # Format response
        response = HealthCheckResponse(
            status=health_status["status"],
            timestamp=health_status["timestamp"],
            checks=health_status["checks"],
            error_statistics=health_status.get("error_statistics")
        )

        return response

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")

        # Return degraded status
        return HealthCheckResponse(
            status="degraded",
            timestamp=datetime.now().isoformat(),
            checks={
                "health_check": {
                    "status": "down",
                    "error": str(e)
                }
            },
            error_statistics=None
        )


# ============================================================
# GET /api/health/detailed - Detailed health with metrics
# ============================================================

@router.get(
    "/health/detailed",
    summary="Detailed health check",
    description="""
    Detailed health check with performance metrics.

    **Includes:**
    - Service health status
    - Error statistics
    - Performance metrics
    - Cache statistics
    - Circuit breaker states (if applicable)

    **Note**: May be slower than basic /health endpoint
    """,
    tags=["Health"]
)
async def detailed_health_check():
    """
    Detailed health check with performance metrics
    """

    error_handler = get_error_handler()
    optimizer = get_performance_optimizer()

    try:
        # Get health status
        health_status = await error_handler.health_check()

        # Get performance report
        performance_report = await optimizer.get_performance_report()

        # Combine data
        detailed_response = {
            "status": health_status["status"],
            "timestamp": health_status["timestamp"],
            "checks": health_status["checks"],
            "error_statistics": health_status.get("error_statistics", {}),
            "performance": {
                "operation_metrics": performance_report.get("operation_metrics", {}),
                "cache_stats": performance_report.get("cache_stats", {}),
                "recommendations": performance_report.get("recommendations", [])
            }
        }

        return detailed_response

    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")

        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


# ============================================================
# GET /api/health/ready - Readiness probe
# ============================================================

@router.get(
    "/health/ready",
    summary="Readiness probe",
    description="""
    Kubernetes readiness probe endpoint.

    **Returns:**
    - 200 OK if ready to accept traffic
    - 503 Service Unavailable if not ready

    **Use Case**: Kubernetes readiness probes
    """,
    tags=["Health"]
)
async def readiness_probe():
    """
    Readiness probe for Kubernetes

    Returns 200 if service is ready to accept traffic
    """

    error_handler = get_error_handler()

    try:
        # Quick health check
        health_status = await error_handler.health_check()

        if health_status["status"] == "healthy":
            return {"ready": True, "timestamp": datetime.now().isoformat()}
        else:
            # Return 503 if not healthy
            from fastapi import Response
            return Response(
                content='{"ready": false}',
                status_code=503,
                media_type="application/json"
            )

    except Exception as e:
        logger.error(f"Readiness probe failed: {str(e)}")
        from fastapi import Response
        return Response(
            content='{"ready": false, "error": "' + str(e) + '"}',
            status_code=503,
            media_type="application/json"
        )


# ============================================================
# GET /api/health/live - Liveness probe
# ============================================================

@router.get(
    "/health/live",
    summary="Liveness probe",
    description="""
    Kubernetes liveness probe endpoint.

    **Returns:**
    - 200 OK if service is alive
    - Used to detect if service needs restart

    **Use Case**: Kubernetes liveness probes
    """,
    tags=["Health"]
)
async def liveness_probe():
    """
    Liveness probe for Kubernetes

    Returns 200 if service is alive (basic check)
    """

    # Simple check - if we can respond, we're alive
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }
