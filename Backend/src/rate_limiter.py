"""
API Rate Limiting Module
Protects API endpoints from abuse and ensures fair usage
"""

import time
from functools import wraps
from typing import Dict, Tuple
from flask import request, jsonify, g
from datetime import datetime, timedelta
import threading


class RateLimiter:
    """Rate limiter for API endpoints"""
    
    def __init__(self):
        """Initialize rate limiter with storage"""
        self.requests = {}  # {ip: [(timestamp, count), ...]}
        self.lock = threading.Lock()
        self.cleanup_interval = 3600  # Clean up every hour
        self.last_cleanup = time.time()
    
    def is_rate_limited(self, ip: str, max_requests: int = 100, window_seconds: int = 3600) -> Tuple[bool, Dict]:
        """
        Check if request from IP is rate limited
        
        Args:
            ip: Client IP address
            max_requests: Max requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            tuple: (is_limited, info_dict)
        """
        with self.lock:
            current_time = time.time()
            
            # Cleanup old entries periodically
            if current_time - self.last_cleanup > self.cleanup_interval:
                self._cleanup_old_requests()
            
            # Initialize IP if not exists
            if ip not in self.requests:
                self.requests[ip] = []
            
            # Remove old requests outside the window
            cutoff_time = current_time - window_seconds
            self.requests[ip] = [req_time for req_time in self.requests[ip] if req_time > cutoff_time]
            
            # Check if limit exceeded
            request_count = len(self.requests[ip])
            is_limited = request_count >= max_requests
            
            # Add current request if not limited
            if not is_limited:
                self.requests[ip].append(current_time)
                request_count += 1
            
            return is_limited, {
                'limit': max_requests,
                'remaining': max(0, max_requests - request_count),
                'reset': datetime.fromtimestamp(current_time + window_seconds).isoformat()
            }
    
    def _cleanup_old_requests(self):
        """Remove old IP entries to prevent memory leak"""
        current_time = time.time()
        ips_to_remove = []
        
        for ip, requests in self.requests.items():
            # Remove IP if no requests in last 24 hours
            if not requests or (current_time - requests[-1]) > 86400:
                ips_to_remove.append(ip)
        
        for ip in ips_to_remove:
            del self.requests[ip]
        
        self.last_cleanup = current_time
    
    def get_client_ip(self) -> str:
        """
        Get client IP from request
        Handles proxies and forwarded headers
        """
        if request.environ.get('HTTP_CF_CONNECTING_IP'):
            return request.environ['HTTP_CF_CONNECTING_IP']
        elif request.environ.get('HTTP_X_FORWARDED_FOR'):
            return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        else:
            return request.remote_addr or '0.0.0.0'


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """
    Decorator to rate limit API endpoints
    
    Args:
        max_requests: Maximum requests allowed in time window
        window_seconds: Time window in seconds (default: 1 hour)
    
    Usage:
        @app.route('/api/endpoint')
        @rate_limit(max_requests=100, window_seconds=3600)
        def my_endpoint():
            return {'data': 'value'}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = _rate_limiter.get_client_ip()
            is_limited, info = _rate_limiter.is_rate_limited(ip, max_requests, window_seconds)
            
            # Add rate limit info to response headers
            g.rate_limit_info = info
            
            if is_limited:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per {window_seconds} seconds',
                    'retry_after': window_seconds
                }), 429  # Too Many Requests
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def add_rate_limit_headers(response):
    """
    Add rate limit headers to response
    Should be registered as after_request handler
    """
    if hasattr(g, 'rate_limit_info'):
        info = g.rate_limit_info
        response.headers['X-RateLimit-Limit'] = str(info['limit'])
        response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
        response.headers['X-RateLimit-Reset'] = info['reset']
    
    return response


# Different rate limit tiers for different endpoints

RATE_LIMITS = {
    'default': {'max_requests': 100, 'window': 3600},      # 100 req/hour
    'strict': {'max_requests': 30, 'window': 3600},        # 30 req/hour
    'moderate': {'max_requests': 200, 'window': 3600},     # 200 req/hour
    'generous': {'max_requests': 500, 'window': 3600},     # 500 req/hour
    'login': {'max_requests': 5, 'window': 900},           # 5 per 15min (prevent brute force)
    'predict': {'max_requests': 50, 'window': 3600},       # 50 per hour
    'export': {'max_requests': 20, 'window': 3600},        # 20 per hour
}


def get_rate_limit_decorator(tier: str = 'default'):
    """Get rate limit decorator for a specific tier"""
    if tier not in RATE_LIMITS:
        tier = 'default'
    
    limits = RATE_LIMITS[tier]
    return rate_limit(max_requests=limits['max_requests'], window_seconds=limits['window'])


# Example usage in Flask app:
# @app.route('/api/login', methods=['POST'])
# @rate_limit(max_requests=5, window_seconds=900)
# def login():
#     # Login logic
#     pass
#
# @app.route('/api/predict', methods=['POST'])
# @get_rate_limit_decorator('predict')
# def predict():
#     # Prediction logic
#     pass
#
# @app.after_request
# def limits(response):
#     return add_rate_limit_headers(response)


class APIUsageAnalytics:
    """Track API usage statistics for monitoring"""
    
    def __init__(self):
        self.endpoint_stats = {}  # {endpoint: {count, errors, avg_response_time}}
        self.lock = threading.Lock()
    
    def record_request(self, endpoint: str, status_code: int, response_time: float):
        """Record API request statistics"""
        with self.lock:
            if endpoint not in self.endpoint_stats:
                self.endpoint_stats[endpoint] = {
                    'count': 0,
                    'errors': 0,
                    'success': 0,
                    'total_time': 0,
                    'avg_time': 0
                }
            
            stats = self.endpoint_stats[endpoint]
            stats['count'] += 1
            stats['total_time'] += response_time
            stats['avg_time'] = stats['total_time'] / stats['count']
            
            if status_code >= 400:
                stats['errors'] += 1
            else:
                stats['success'] += 1
    
    def get_stats(self, endpoint: str = None) -> Dict:
        """Get API statistics"""
        with self.lock:
            if endpoint:
                return self.endpoint_stats.get(endpoint, {})
            return self.endpoint_stats
    
    def get_summary(self) -> Dict:
        """Get summary statistics across all endpoints"""
        with self.lock:
            total_requests = sum(s['count'] for s in self.endpoint_stats.values())
            total_errors = sum(s['errors'] for s in self.endpoint_stats.values())
            avg_response_time = sum(s['avg_time'] for s in self.endpoint_stats.values()) / len(self.endpoint_stats) if self.endpoint_stats else 0
            
            return {
                'total_requests': total_requests,
                'total_errors': total_errors,
                'success_rate': (total_requests - total_errors) / total_requests if total_requests > 0 else 0,
                'average_response_time': avg_response_time,
                'endpoints': len(self.endpoint_stats)
            }


# Global analytics instance
api_analytics = APIUsageAnalytics()
