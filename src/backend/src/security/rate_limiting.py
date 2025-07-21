"""
Rate Limiting Manager for Intelligence OS
Implements comprehensive rate limiting for API endpoints
"""

import os
import time
import redis
from flask import request, jsonify, current_app
from functools import wraps
from typing import Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Comprehensive rate limiting manager"""
    
    def __init__(self, app=None, redis_client=None):
        self.app = app
        self.redis_client = redis_client
        self.enabled = True
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize rate limiter with Flask app"""
        self.app = app
        self.enabled = app.config.get('RATE_LIMIT_ENABLED', True)
        
        if self.enabled:
            # Initialize Redis connection
            redis_url = os.getenv('RATE_LIMIT_STORAGE_URL', os.getenv('REDIS_URL', 'redis://localhost:6379/1'))
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()  # Test connection
                logger.info("Rate limiter initialized with Redis backend")
            except Exception as e:
                logger.warning(f"Redis connection failed, using in-memory storage: {str(e)}")
                self.redis_client = None
                self._memory_store = {}
        else:
            logger.info("Rate limiting disabled")
    
    def _get_client_id(self) -> str:
        """Get unique client identifier"""
        # Try to get user ID from JWT token
        from flask import g
        if hasattr(g, 'current_user_id') and g.current_user_id:
            return f"user:{g.current_user_id}"
        
        # Fall back to IP address
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        return f"ip:{client_ip}"
    
    def _get_key(self, identifier: str, window: int) -> str:
        """Generate Redis key for rate limiting"""
        timestamp = int(time.time() // window)
        return f"rate_limit:{identifier}:{timestamp}"
    
    def _check_rate_limit_redis(self, key: str, limit: int, window: int) -> Dict:
        """Check rate limit using Redis backend"""
        try:
            current_count = self.redis_client.get(key)
            if current_count is None:
                # First request in this window
                self.redis_client.setex(key, window, 1)
                return {
                    'allowed': True,
                    'count': 1,
                    'limit': limit,
                    'remaining': limit - 1,
                    'reset_time': int(time.time()) + window
                }
            
            current_count = int(current_count)
            if current_count >= limit:
                # Rate limit exceeded
                ttl = self.redis_client.ttl(key)
                return {
                    'allowed': False,
                    'count': current_count,
                    'limit': limit,
                    'remaining': 0,
                    'reset_time': int(time.time()) + ttl
                }
            
            # Increment counter
            new_count = self.redis_client.incr(key)
            return {
                'allowed': True,
                'count': new_count,
                'limit': limit,
                'remaining': limit - new_count,
                'reset_time': int(time.time()) + self.redis_client.ttl(key)
            }
            
        except Exception as e:
            logger.error(f"Redis rate limiting error: {str(e)}")
            # Allow request if Redis fails
            return {
                'allowed': True,
                'count': 0,
                'limit': limit,
                'remaining': limit,
                'reset_time': int(time.time()) + window
            }
    
    def _check_rate_limit_memory(self, key: str, limit: int, window: int) -> Dict:
        """Check rate limit using in-memory storage"""
        current_time = time.time()
        window_start = int(current_time // window) * window
        
        if key not in self._memory_store:
            self._memory_store[key] = {'count': 0, 'window_start': window_start}
        
        entry = self._memory_store[key]
        
        # Reset if new window
        if entry['window_start'] < window_start:
            entry['count'] = 0
            entry['window_start'] = window_start
        
        if entry['count'] >= limit:
            return {
                'allowed': False,
                'count': entry['count'],
                'limit': limit,
                'remaining': 0,
                'reset_time': int(window_start + window)
            }
        
        entry['count'] += 1
        return {
            'allowed': True,
            'count': entry['count'],
            'limit': limit,
            'remaining': limit - entry['count'],
            'reset_time': int(window_start + window)
        }
    
    def check_rate_limit(self, identifier: str, limit: int, window: int) -> Dict:
        """Check if request is within rate limit"""
        if not self.enabled:
            return {
                'allowed': True,
                'count': 0,
                'limit': limit,
                'remaining': limit,
                'reset_time': int(time.time()) + window
            }
        
        key = self._get_key(identifier, window)
        
        if self.redis_client:
            return self._check_rate_limit_redis(key, limit, window)
        else:
            return self._check_rate_limit_memory(key, limit, window)
    
    def limit(self, rate: str, per_user: bool = True, key_func: Optional[Callable] = None):
        """
        Rate limiting decorator
        
        Args:
            rate: Rate limit string (e.g., "100 per hour", "10 per minute")
            per_user: If True, limit per user; if False, limit per IP
            key_func: Custom function to generate rate limit key
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.enabled:
                    return f(*args, **kwargs)
                
                # Parse rate string
                try:
                    parts = rate.lower().split()
                    limit = int(parts[0])
                    
                    if 'second' in parts[-1]:
                        window = 1
                    elif 'minute' in parts[-1]:
                        window = 60
                    elif 'hour' in parts[-1]:
                        window = 3600
                    elif 'day' in parts[-1]:
                        window = 86400
                    else:
                        window = 3600  # Default to 1 hour
                        
                except (ValueError, IndexError):
                    logger.error(f"Invalid rate limit format: {rate}")
                    return f(*args, **kwargs)
                
                # Generate identifier
                if key_func:
                    identifier = key_func()
                elif per_user:
                    identifier = self._get_client_id()
                else:
                    identifier = f"global:{request.endpoint}"
                
                # Check rate limit
                result = self.check_rate_limit(identifier, limit, window)
                
                if not result['allowed']:
                    response = jsonify({
                        'success': False,
                        'error': 'rate_limit_exceeded',
                        'message': f'Rate limit exceeded. Try again in {result["reset_time"] - int(time.time())} seconds.',
                        'rate_limit': {
                            'limit': result['limit'],
                            'remaining': result['remaining'],
                            'reset_time': result['reset_time']
                        }
                    })
                    response.status_code = 429
                    response.headers['X-RateLimit-Limit'] = str(result['limit'])
                    response.headers['X-RateLimit-Remaining'] = str(result['remaining'])
                    response.headers['X-RateLimit-Reset'] = str(result['reset_time'])
                    response.headers['Retry-After'] = str(result['reset_time'] - int(time.time()))
                    return response
                
                # Add rate limit headers to successful responses
                response = f(*args, **kwargs)
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(result['limit'])
                    response.headers['X-RateLimit-Remaining'] = str(result['remaining'])
                    response.headers['X-RateLimit-Reset'] = str(result['reset_time'])
                
                return response
            
            return decorated_function
        return decorator
    
    def exempt(self, f: Callable) -> Callable:
        """Decorator to exempt a route from rate limiting"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        
        decorated_function._rate_limit_exempt = True
        return decorated_function

# Global rate limiter instance
rate_limiter = RateLimiter()