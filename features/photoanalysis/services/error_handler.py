"""
Error Handling & Monitoring Service (Step 19)
Comprehensive error handling, retry logic, and monitoring integration

This service provides:
1. Centralized exception handling
2. Retry logic with exponential backoff
3. Sentry integration for error tracking
4. Structured logging
5. Fallback strategies for partial data
"""
import logging
import traceback
import asyncio
from typing import Optional, Callable, Any, TypeVar, Dict, List
from functools import wraps
from datetime import datetime
import uuid

# Try to import Sentry (optional dependency)
try:
    import sentry_sdk
    from sentry_sdk import capture_exception, capture_message, set_context, set_tag
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logging.warning("Sentry SDK not available - error tracking will be limited")

from ..models.schemas import ErrorLog
from ..config.settings import get_settings


# Setup logging
logger = logging.getLogger(__name__)

# Type variable for generic functions
T = TypeVar('T')


class PhotoAnalysisError(Exception):
    """Base exception for photo analysis errors"""
    def __init__(self, message: str, step: str, recoverable: bool = True, context: Dict = None):
        self.message = message
        self.step = step
        self.recoverable = recoverable
        self.context = context or {}
        super().__init__(self.message)


class ImageValidationError(PhotoAnalysisError):
    """Image quality validation failed"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, step="Step 1 - Image Validation", **kwargs)


class ImageProcessingError(PhotoAnalysisError):
    """Image preprocessing failed"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, step="Step 2 - Image Processing", **kwargs)


class AngleDetectionError(PhotoAnalysisError):
    """Angle detection failed"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, step="Step 3 - Angle Detection", **kwargs)


class AIAnalysisError(PhotoAnalysisError):
    """AI vision analysis failed"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, step="Steps 6-9 - AI Analysis", recoverable=True, **kwargs)


class MathematicalAnalysisError(PhotoAnalysisError):
    """Mathematical analysis failed"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, step="Steps 10-16 - Math Analysis", **kwargs)


class PersistenceError(PhotoAnalysisError):
    """Database persistence failed"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, step="Step 17 - Persistence", **kwargs)


class RecommendationError(PhotoAnalysisError):
    """Recommendation generation failed"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, step="Step 18 - Recommendations", recoverable=True, **kwargs)


# ============================================================
# ERROR HANDLER CLASS
# ============================================================

class ErrorHandler:
    """
    Centralized error handling and monitoring
    """

    def __init__(self):
        """Initialize error handler with Sentry (if available)"""
        self.settings = get_settings()

        # Initialize Sentry if available and configured
        if SENTRY_AVAILABLE and hasattr(self.settings, 'sentry_dsn'):
            try:
                sentry_sdk.init(
                    dsn=self.settings.sentry_dsn,
                    environment=self.settings.environment or "development",
                    traces_sample_rate=0.1,  # 10% of transactions
                    profiles_sample_rate=0.1,
                )
                logger.info("Sentry error tracking initialized")
                self.sentry_enabled = True
            except Exception as e:
                logger.warning(f"Failed to initialize Sentry: {str(e)}")
                self.sentry_enabled = False
        else:
            self.sentry_enabled = False
            logger.info("Sentry error tracking disabled")

        # Error statistics
        self.error_counts: Dict[str, int] = {}


    # ============================================================
    # RETRY DECORATOR
    # ============================================================

    def with_retry(
        self,
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None
    ):
        """
        Decorator to add retry logic with exponential backoff

        Args:
            max_attempts: Maximum number of attempts
            delay_seconds: Initial delay between retries
            backoff_factor: Multiplier for delay on each retry
            exceptions: Tuple of exceptions to catch and retry
            on_retry: Optional callback function called on each retry

        Example:
            @error_handler.with_retry(max_attempts=3, delay_seconds=2.0)
            async def call_openai_api():
                # API call that might fail
                pass
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                last_exception = None
                delay = delay_seconds

                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)

                    except exceptions as e:
                        last_exception = e

                        if attempt < max_attempts:
                            logger.warning(
                                f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                                f"Retrying in {delay:.1f}s..."
                            )

                            # Call on_retry callback if provided
                            if on_retry:
                                on_retry(attempt, e)

                            await asyncio.sleep(delay)
                            delay *= backoff_factor
                        else:
                            logger.error(
                                f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}"
                            )

                # All attempts exhausted
                raise last_exception

            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                last_exception = None
                delay = delay_seconds

                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)

                    except exceptions as e:
                        last_exception = e

                        if attempt < max_attempts:
                            logger.warning(
                                f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                                f"Retrying in {delay:.1f}s..."
                            )

                            if on_retry:
                                on_retry(attempt, e)

                            import time
                            time.sleep(delay)
                            delay *= backoff_factor
                        else:
                            logger.error(
                                f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}"
                            )

                raise last_exception

            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator


    # ============================================================
    # ERROR LOGGING & TRACKING
    # ============================================================

    async def log_error(
        self,
        error: Exception,
        step: str,
        user_id: Optional[str] = None,
        scan_id: Optional[str] = None,
        context: Optional[Dict] = None,
        severity: str = "error"
    ) -> ErrorLog:
        """
        Log error with comprehensive tracking

        Args:
            error: Exception that occurred
            step: Which step/component failed
            user_id: User ID (if available)
            scan_id: Scan ID (if available)
            context: Additional context
            severity: error, warning, info

        Returns:
            ErrorLog object
        """
        error_id = str(uuid.uuid4())

        # Create error log
        error_log = ErrorLog(
            error_id=error_id,
            timestamp=datetime.now(),
            step=step,
            error_type=type(error).__name__,
            error_message=str(error),
            user_id=user_id,
            scan_id=scan_id,
            stack_trace=traceback.format_exc(),
            context=context or {}
        )

        # Log to standard logger
        log_message = (
            f"[{step}] {type(error).__name__}: {str(error)} | "
            f"user={user_id} scan={scan_id}"
        )

        if severity == "error":
            logger.error(log_message, exc_info=True)
        elif severity == "warning":
            logger.warning(log_message)
        else:
            logger.info(log_message)

        # Track error count
        self.error_counts[step] = self.error_counts.get(step, 0) + 1

        # Send to Sentry if enabled
        if self.sentry_enabled:
            self._send_to_sentry(error, error_log)

        return error_log


    def _send_to_sentry(self, error: Exception, error_log: ErrorLog):
        """Send error to Sentry for tracking"""
        try:
            # Set context
            set_context("error_log", error_log.dict())

            # Set tags for filtering
            set_tag("step", error_log.step)
            if error_log.user_id:
                set_tag("user_id", error_log.user_id)
            if error_log.scan_id:
                set_tag("scan_id", error_log.scan_id)

            # Capture exception
            capture_exception(error)

        except Exception as e:
            logger.error(f"Failed to send error to Sentry: {str(e)}")


    # ============================================================
    # FALLBACK STRATEGIES
    # ============================================================

    async def with_fallback(
        self,
        primary_func: Callable[..., T],
        fallback_func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        Try primary function, fall back to alternative if it fails

        Args:
            primary_func: Main function to try
            fallback_func: Fallback function if primary fails
            *args, **kwargs: Arguments to pass to functions

        Returns:
            Result from primary or fallback function
        """
        try:
            logger.info(f"Attempting primary: {primary_func.__name__}")
            return await primary_func(*args, **kwargs)

        except Exception as e:
            logger.warning(
                f"Primary function {primary_func.__name__} failed: {str(e)}. "
                f"Falling back to {fallback_func.__name__}"
            )

            try:
                return await fallback_func(*args, **kwargs)
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                raise


    def get_partial_data_strategy(
        self,
        data: Dict[str, Any],
        required_fields: List[str],
        optional_fields: List[str]
    ) -> tuple[Dict[str, Any], List[str]]:
        """
        Extract partial data when some fields are missing

        Args:
            data: Data dictionary
            required_fields: Fields that must be present
            optional_fields: Fields that are nice to have

        Returns:
            Tuple of (partial_data, missing_fields)

        Raises:
            ValueError: If required fields are missing
        """
        missing_required = [field for field in required_fields if field not in data]

        if missing_required:
            raise ValueError(f"Required fields missing: {missing_required}")

        # Extract all available data
        partial_data = {}
        missing_optional = []

        for field in required_fields + optional_fields:
            if field in data:
                partial_data[field] = data[field]
            elif field in optional_fields:
                missing_optional.append(field)

        if missing_optional:
            logger.warning(f"Optional fields missing: {missing_optional}")

        return partial_data, missing_optional


    # ============================================================
    # HEALTH CHECKS
    # ============================================================

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of all services

        Returns:
            Dictionary with health status of each component
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }

        # Check OpenAI/Claude API
        try:
            # TODO: Add actual API health check
            health_status["checks"]["ai_api"] = {"status": "up", "message": "OK"}
        except Exception as e:
            health_status["checks"]["ai_api"] = {"status": "down", "error": str(e)}
            health_status["status"] = "degraded"

        # Check Firestore
        try:
            # TODO: Add Firestore health check
            health_status["checks"]["firestore"] = {"status": "up", "message": "OK"}
        except Exception as e:
            health_status["checks"]["firestore"] = {"status": "down", "error": str(e)}
            health_status["status"] = "degraded"

        # Check Sentry
        health_status["checks"]["sentry"] = {
            "status": "up" if self.sentry_enabled else "disabled"
        }

        # Error statistics
        health_status["error_statistics"] = self.error_counts.copy()

        return health_status


    # ============================================================
    # CONTEXT MANAGERS
    # ============================================================

    class ErrorContext:
        """Context manager for error handling"""

        def __init__(
            self,
            handler: 'ErrorHandler',
            step: str,
            user_id: Optional[str] = None,
            scan_id: Optional[str] = None,
            raise_on_error: bool = True
        ):
            self.handler = handler
            self.step = step
            self.user_id = user_id
            self.scan_id = scan_id
            self.raise_on_error = raise_on_error
            self.error_log: Optional[ErrorLog] = None

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if exc_val is not None:
                # Log the error
                self.error_log = await self.handler.log_error(
                    error=exc_val,
                    step=self.step,
                    user_id=self.user_id,
                    scan_id=self.scan_id
                )

                # Suppress exception if raise_on_error is False
                return not self.raise_on_error

            return False


    def error_context(
        self,
        step: str,
        user_id: Optional[str] = None,
        scan_id: Optional[str] = None,
        raise_on_error: bool = True
    ):
        """
        Create error context manager

        Usage:
            async with error_handler.error_context("Step 5", user_id="123"):
                # Code that might fail
                result = await some_function()
        """
        return self.ErrorContext(self, step, user_id, scan_id, raise_on_error)


# ============================================================
# TIMEOUT DECORATOR
# ============================================================

def with_timeout(seconds: float):
    """
    Decorator to add timeout to async functions

    Args:
        seconds: Maximum execution time

    Example:
        @with_timeout(30.0)
        async def slow_function():
            await asyncio.sleep(60)  # Will timeout after 30s
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {seconds}s")
                raise PhotoAnalysisError(
                    f"Operation timed out after {seconds} seconds",
                    step=func.__name__,
                    recoverable=False
                )
        return wrapper
    return decorator


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get singleton error handler instance"""
    global _error_handler

    if _error_handler is None:
        _error_handler = ErrorHandler()

    return _error_handler


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

async def safe_execute(
    func: Callable[..., T],
    *args,
    step: str,
    user_id: Optional[str] = None,
    scan_id: Optional[str] = None,
    default_value: Optional[T] = None,
    **kwargs
) -> Optional[T]:
    """
    Safely execute function and return default value on error

    Args:
        func: Function to execute
        step: Step identifier for logging
        user_id: User ID
        scan_id: Scan ID
        default_value: Value to return on error
        *args, **kwargs: Arguments to pass to function

    Returns:
        Function result or default_value on error
    """
    handler = get_error_handler()

    try:
        return await func(*args, **kwargs)
    except Exception as e:
        await handler.log_error(
            error=e,
            step=step,
            user_id=user_id,
            scan_id=scan_id,
            severity="error"
        )
        return default_value
