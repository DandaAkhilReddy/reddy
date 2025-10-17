"""
Rate Limiting Middleware - Prevent API abuse
"""
import logging
import time
from typing import Dict
from collections import defaultdict, deque
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    In-memory rate limiting middleware

    **Features:**
    - Per-IP rate limiting
    - Sliding window algorithm
    - Configurable requests per minute
    - Returns 429 Too Many Requests when exceeded

    **Headers Added:**
    - X-RateLimit-Limit: Max requests per window
    - X-RateLimit-Remaining: Requests remaining
    - X-RateLimit-Reset: Time until window reset (seconds)

    **Production Note:**
    For distributed systems, use Redis-based rate limiting
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        window_size_seconds: int = 60
    ):
        """
        Initialize rate limiter

        Args:
            app: FastAPI application
            requests_per_minute: Max requests per minute (default: 60)
            window_size_seconds: Time window in seconds (default: 60)
        """
        super().__init__(app)

        self.requests_per_minute = requests_per_minute
        self.window_size = window_size_seconds

        # In-memory storage: {client_ip: deque of timestamps}
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque())

        logger.info(
            f"Rate limiter initialized: {requests_per_minute} requests per {window_size_seconds}s"
        )


    async def dispatch(self, request: Request, call_next):
        """
        Middleware dispatch - check rate limit on each request
        """

        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)

        # Current timestamp
        now = time.time()

        # Get request history for this client
        timestamps = self.request_history[client_ip]

        # Remove old timestamps outside the window
        cutoff_time = now - self.window_size
        while timestamps and timestamps[0] < cutoff_time:
            timestamps.popleft()

        # Check if limit exceeded
        if len(timestamps) >= self.requests_per_minute:
            # Rate limit exceeded
            oldest_timestamp = timestamps[0]
            reset_time = int(oldest_timestamp + self.window_size - now)

            logger.warning(
                f"Rate limit exceeded for {client_ip}: "
                f"{len(timestamps)}/{self.requests_per_minute} requests"
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded. Max {self.requests_per_minute} requests per minute.",
                    "retry_after": reset_time
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time)
                }
            )

        # Record this request
        timestamps.append(now)

        # Calculate remaining requests
        remaining = self.requests_per_minute - len(timestamps)

        # Continue to endpoint
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(self.window_size))

        return response


    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request

        Checks for X-Forwarded-For header (reverse proxy)
        Falls back to client.host

        Args:
            request: FastAPI request

        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (if behind reverse proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs
            # Take the first one (original client)
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        # Default fallback
        return "unknown"


    def clear_history(self):
        """
        Clear rate limit history

        Useful for testing or manual reset
        """
        self.request_history.clear()
        logger.info("Rate limit history cleared")


    def get_client_stats(self, client_ip: str) -> Dict:
        """
        Get rate limit statistics for a client

        Args:
            client_ip: Client IP address

        Returns:
            Dictionary with stats
        """
        timestamps = self.request_history.get(client_ip, deque())

        # Remove old timestamps
        now = time.time()
        cutoff_time = now - self.window_size

        valid_timestamps = [ts for ts in timestamps if ts >= cutoff_time]

        return {
            "client_ip": client_ip,
            "requests_in_window": len(valid_timestamps),
            "limit": self.requests_per_minute,
            "remaining": self.requests_per_minute - len(valid_timestamps),
            "window_size_seconds": self.window_size
        }


# ============================================================
# REDIS-BASED RATE LIMITER (Production)
# ============================================================

# Try to import Redis
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.info("Redis not available - using in-memory rate limiter")


class RedisRateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware (for production)

    **Advantages over in-memory:**
    - Distributed rate limiting across multiple API instances
    - Persistent across restarts
    - Better performance at scale

    **Requires:**
    - Redis server
    - redis-py package
    """

    def __init__(
        self,
        app,
        redis_url: str,
        requests_per_minute: int = 60,
        window_size_seconds: int = 60
    ):
        """
        Initialize Redis-based rate limiter

        Args:
            app: FastAPI application
            redis_url: Redis connection URL
            requests_per_minute: Max requests per minute
            window_size_seconds: Time window in seconds
        """
        super().__init__(app)

        if not REDIS_AVAILABLE:
            raise ImportError("Redis not available. Install with: pip install redis")

        self.requests_per_minute = requests_per_minute
        self.window_size = window_size_seconds

        # Initialize Redis connection
        self.redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)

        logger.info(f"Redis rate limiter initialized: {redis_url}")


    async def dispatch(self, request: Request, call_next):
        """
        Middleware dispatch with Redis
        """

        client_ip = self._get_client_ip(request)

        # Redis key for this client
        redis_key = f"ratelimit:{client_ip}"

        try:
            # Use Redis sorted set with timestamps as scores
            now = time.time()
            cutoff_time = now - self.window_size

            # Remove old entries
            await self.redis_client.zremrangebyscore(redis_key, 0, cutoff_time)

            # Count current requests in window
            count = await self.redis_client.zcard(redis_key)

            if count >= self.requests_per_minute:
                # Rate limit exceeded
                oldest = await self.redis_client.zrange(redis_key, 0, 0, withscores=True)
                if oldest:
                    oldest_timestamp = oldest[0][1]
                    reset_time = int(oldest_timestamp + self.window_size - now)
                else:
                    reset_time = self.window_size

                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Too Many Requests",
                        "message": f"Rate limit exceeded. Max {self.requests_per_minute} requests per minute.",
                        "retry_after": reset_time
                    },
                    headers={
                        "X-RateLimit-Limit": str(self.requests_per_minute),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_time),
                        "Retry-After": str(reset_time)
                    }
                )

            # Add current request
            await self.redis_client.zadd(redis_key, {str(now): now})

            # Set expiry on key
            await self.redis_client.expire(redis_key, self.window_size)

            remaining = self.requests_per_minute - (count + 1)

            # Continue to endpoint
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(self.window_size)

            return response

        except Exception as e:
            logger.error(f"Redis rate limiter error: {str(e)}")
            # Fall back to allowing request on Redis error
            return await call_next(request)


    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        if request.client:
            return request.client.host

        return "unknown"
