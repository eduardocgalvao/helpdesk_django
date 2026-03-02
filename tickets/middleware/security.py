"""
Security Middleware

Handles:
- Rate limiting
- CORS security
- Request validation
- Attack prevention (SQL injection, XSS, etc.)
- Security headers
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('helpdesk.security')


class RateLimitingMiddleware(MiddlewareMixin):
    """
    Implement rate limiting to prevent abuse.
    
    Configuration:
    - Anonymous users: 30 requests per minute
    - Authenticated users: 100 requests per minute
    - Admin users: 500 requests per minute
    """
    
    # Rate limits per minute
    RATE_LIMITS = {
        'anonymous': 30,
        'authenticated': 100,
        'admin': 500,
    }
    
    # Blacklist duration in seconds
    BLACKLIST_DURATION = 3600  # 1 hour
    
    def process_request(self, request):
        """
        Check and enforce rate limits.
        """
        client_ip = self.get_client_ip(request)
        
        # Check if IP is blacklisted
        blacklist_key = f"rate_limit_blacklist:{client_ip}"
        if cache.get(blacklist_key):
            logger.warning(f"Blacklisted IP attempted access: {client_ip}")
            return JsonResponse(
                {'error': 'Too many requests. Access denied.'},
                status=429
            )
        
        # Determine rate limit based on user type
        if request.user.is_authenticated:
            limit = self.RATE_LIMITS['admin'] if request.user.is_superuser else self.RATE_LIMITS['authenticated']
            user_identifier = f"rate_limit:{request.user.id}"
        else:
            limit = self.RATE_LIMITS['anonymous']
            user_identifier = f"rate_limit:{client_ip}"
        
        # Get current request count
        key = f"{user_identifier}:{int(time.time() // 60)}"
        request_count = cache.get(key, 0)
        
        # Increment and set expiry
        cache.set(key, request_count + 1, 60)
        
        # Check if limit exceeded
        if request_count >= limit:
            logger.warning(
                f"Rate limit exceeded for {user_identifier} "
                f"({request_count}/{limit} requests)"
            )
            
            # Blacklist on repeated violations
            violation_key = f"rate_limit_violations:{user_identifier}"
            violations = cache.get(violation_key, 0)
            cache.set(violation_key, violations + 1, 60)
            
            if violations > 3:
                cache.set(blacklist_key, True, self.BLACKLIST_DURATION)
                logger.error(f"IP blacklisted due to repeated violations: {user_identifier}")
            
            return JsonResponse(
                {'error': 'Rate limit exceeded. Maximum {} requests per minute.'.format(limit)},
                status=429
            )
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses.
    """
    
    def process_response(self, request, response):
        """
        Add security headers to response.
        """
        # Prevent clickjacking
        response['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevent MIME sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'self';"
        )
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'gyroscope=(), '
            'accelerometer=()'
        )
        
        # HSTS (only in production)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Validate incoming requests for basic security checks.
    """
    
    # Maximum request body size (10 MB)
    MAX_BODY_SIZE = 10 * 1024 * 1024
    
    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = [
        '<script',
        'javascript:',
        'onerror=',
        'onload=',
        'onclick=',
        'DROP TABLE',
        'DELETE FROM',
        'UNION SELECT',
        'exec(',
        'eval(',
    ]
    
    def process_request(self, request):
        """
        Validate request before processing.
        """
        # Check request body size
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            logger.warning(
                f"Request body too large from {self.get_client_ip(request)}: "
                f"{content_length} bytes"
            )
            return HttpResponse('Request body too large', status=413)
        
        # Check for suspicious content in GET parameters
        if request.GET:
            query_string = request.META.get('QUERY_STRING', '')
            if self.contains_suspicious_content(query_string):
                logger.warning(
                    f"Suspicious GET request from {self.get_client_ip(request)}: "
                    f"{query_string[:100]}"
                )
                return HttpResponse('Suspicious request detected', status=400)
        
        return None
    
    def contains_suspicious_content(self, text):
        """
        Check if text contains suspicious patterns.
        """
        text_upper = text.upper()
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.upper() in text_upper:
                return True
        return False
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CORSMiddleware(MiddlewareMixin):
    """
    Handle CORS (Cross-Origin Resource Sharing) requests.
    """
    
    # Allowed origins
    ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:8000',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:8000',
    ]
    
    def process_request(self, request):
        """
        Handle preflight requests.
        """
        if request.method == 'OPTIONS':
            return self.preflight_response(request)
        return None
    
    def process_response(self, request, response):
        """
        Add CORS headers to response.
        """
        origin = request.META.get('HTTP_ORIGIN')
        
        if origin in self.ALLOWED_ORIGINS:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Max-Age'] = '3600'
        
        return response
    
    def preflight_response(self, request):
        """
        Return preflight response for OPTIONS requests.
        """
        response = HttpResponse()
        origin = request.META.get('HTTP_ORIGIN')
        
        if origin in self.ALLOWED_ORIGINS:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Max-Age'] = '3600'
        
        response.status_code = 204
        return response
