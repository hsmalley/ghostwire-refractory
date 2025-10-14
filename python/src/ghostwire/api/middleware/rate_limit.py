"""
Rate limiting middleware for GhostWire Refractory
"""
import time
from typing import Dict
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent API abuse"""
    
    def __init__(self, app, requests: int = 100, window: int = 60):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.requests_log: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP address
        client_ip = request.client.host
        
        # Clean old requests outside the current window
        current_time = time.time()
        self.requests_log[client_ip] = [
            req_time for req_time in self.requests_log[client_ip]
            if current_time - req_time < self.window
        ]
        
        # Check if client has exceeded the rate limit
        if len(self.requests_log[client_ip]) >= self.requests:
            return Response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content="Rate limit exceeded"
            )
        
        # Add current request to log
        self.requests_log[client_ip].append(current_time)
        
        # Continue with the request
        response = await call_next(request)
        return response