"""
API Middleware - Request/Response middleware and security
"""
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Duration: {process_time:.2f}s"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    """
    
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            ip: timestamps 
            for ip, timestamps in self.requests.items() 
            if any(t > current_time - self.window for t in timestamps)
        }
        
        # Check rate limit
        if client_ip in self.requests:
            timestamps = [
                t for t in self.requests[client_ip] 
                if t > current_time - self.window
            ]
            
            if len(timestamps) >= self.max_requests:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return Response(
                    content="Rate limit exceeded",
                    status_code=429
                )
            
            timestamps.append(current_time)
            self.requests[client_ip] = timestamps
        else:
            self.requests[client_ip] = [current_time]
        
        return await call_next(request)


def setup_middleware(app):
    """
    Configure all middleware for the application
    """
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware (uncomment for production)
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=["localhost", "127.0.0.1"]
    # )
    
    # Custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)
    
    logger.info("Middleware configured successfully")
