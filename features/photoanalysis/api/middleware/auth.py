"""
Authentication Middleware - Firebase Auth JWT validation
"""
import logging
from typing import List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import re

# Try to import Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import auth, credentials
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("Firebase Admin SDK not available - auth middleware will run in mock mode")

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Firebase Authentication Middleware

    Validates JWT tokens on all requests except excluded paths.

    **Features:**
    - Firebase JWT token validation
    - Extract user_id from token
    - Add user context to request state
    - Exclude public paths (/health, /docs)

    **Headers:**
    - Authorization: Bearer <firebase_jwt_token>

    **Mock Mode:**
    If Firebase SDK not available, runs in mock mode (accepts any token)
    """

    def __init__(self, app, exclude_paths: List[str] = None):
        """
        Initialize auth middleware

        Args:
            app: FastAPI application
            exclude_paths: List of paths to exclude from auth (regex patterns)
        """
        super().__init__(app)

        self.exclude_paths = exclude_paths or []

        # Initialize Firebase (if available)
        if FIREBASE_AVAILABLE:
            try:
                # Check if Firebase app is already initialized
                try:
                    firebase_admin.get_app()
                    logger.info("Firebase already initialized")
                except ValueError:
                    # Initialize Firebase
                    # Note: In production, use service account credentials
                    # For now, using default credentials
                    firebase_admin.initialize_app()
                    logger.info("Firebase Admin SDK initialized for auth")

                self.firebase_enabled = True

            except Exception as e:
                logger.warning(f"Failed to initialize Firebase: {str(e)}. Running in mock mode.")
                self.firebase_enabled = False
        else:
            self.firebase_enabled = False
            logger.info("Auth middleware running in MOCK mode (Firebase not available)")


    async def dispatch(self, request: Request, call_next):
        """
        Middleware dispatch - validate auth on each request
        """

        # Check if path is excluded
        if self._is_excluded_path(request.url.path):
            # Skip auth for excluded paths
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            # No auth header - return 401
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Unauthorized",
                    "message": "Missing Authorization header. Include 'Authorization: Bearer <token>'"
                }
            )

        # Parse token
        try:
            # Expected format: "Bearer <token>"
            parts = auth_header.split()

            if len(parts) != 2 or parts[0].lower() != "bearer":
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": "Unauthorized",
                        "message": "Invalid Authorization header format. Use 'Bearer <token>'"
                    }
                )

            token = parts[1]

            # Verify token
            if self.firebase_enabled:
                # Production: Verify with Firebase
                try:
                    decoded_token = auth.verify_id_token(token)
                    user_id = decoded_token.get("uid")

                    # Add user to request state
                    request.state.user_id = user_id
                    request.state.user_email = decoded_token.get("email")

                    logger.debug(f"Authenticated user: {user_id}")

                except Exception as e:
                    logger.warning(f"Token verification failed: {str(e)}")
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={
                            "error": "Unauthorized",
                            "message": "Invalid or expired token"
                        }
                    )

            else:
                # Mock mode: Accept any token, extract user_id from token
                # Format: "mock_user_<user_id>" or just use token as user_id
                user_id = token if token.startswith("mock_user_") else f"mock_user_{token[:12]}"

                request.state.user_id = user_id
                request.state.user_email = f"{user_id}@mock.com"

                logger.debug(f"Mock auth: {user_id}")

        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": "Authentication processing failed"
                }
            )

        # Continue to endpoint
        response = await call_next(request)
        return response


    def _is_excluded_path(self, path: str) -> bool:
        """
        Check if path is excluded from authentication

        Args:
            path: Request path

        Returns:
            True if path is excluded
        """
        for pattern in self.exclude_paths:
            if re.match(pattern, path):
                return True

        return False


# ============================================================
# DEPENDENCY: Get current user from request
# ============================================================

def get_current_user(request: Request) -> str:
    """
    Dependency to extract current user from request state

    Usage:
        @router.get("/endpoint")
        async def endpoint(user_id: str = Depends(get_current_user)):
            # user_id is authenticated user

    Args:
        request: FastAPI request

    Returns:
        user_id from token

    Raises:
        HTTPException: If user not authenticated
    """
    user_id = getattr(request.state, "user_id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return user_id


def get_current_user_email(request: Request) -> str:
    """
    Dependency to extract current user email from request state

    Args:
        request: FastAPI request

    Returns:
        user_email from token
    """
    user_email = getattr(request.state, "user_email", None)

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return user_email
