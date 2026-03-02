"""
Logging Middleware

Handles:
- Request/Response logging
- User activity tracking
- Performance monitoring
- Error logging
"""

import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse

logger = logging.getLogger('helpdesk.middleware')
activity_logger = logging.getLogger('helpdesk.activity')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all incoming requests with details.
    """
    
    # HTTP methods to log
    LOGGABLE_METHODS = ['POST', 'PUT', 'DELETE', 'PATCH']
    
    # Sensitive fields to mask in logs
    SENSITIVE_FIELDS = ['password', 'token', 'secret', 'api_key', 'credit_card']
    
    def process_request(self, request):
        """
        Log incoming request details.
        """
        # Store request start time for performance tracking
        request._start_time = time.time()
        
        # Log request info
        method = request.method
        path = request.path
        user = request.user.username if not isinstance(request.user, AnonymousUser) else 'Anonymous'
        ip = self.get_client_ip(request)
        
        # Log GET requests with limited detail
        if method == 'GET':
            logger.debug(f"{method} {path} by {user} from {ip}")
        
        # Log form data for POST/PUT/PATCH/DELETE
        elif method in self.LOGGABLE_METHODS:
            body = self.mask_sensitive_data(request.POST.dict())
            logger.info(f"{method} {path} by {user} | Data: {body} | IP: {ip}")
            
            # Track user activity
            activity_logger.info(
                f"ACTION | User: {user} | Action: {method} {path} | IP: {ip}"
            )
        
        return None
    
    def process_response(self, request, response):
        """
        Log response details and performance metrics.
        """
        if hasattr(request, '_start_time'):
            elapsed_time = time.time() - request._start_time
            status_code = response.status_code
            method = request.method
            path = request.path
            user = request.user.username if not isinstance(request.user, AnonymousUser) else 'Anonymous'
            
            # Log slow requests (> 1 second)
            if elapsed_time > 1.0:
                logger.warning(
                    f"SLOW REQUEST | {method} {path} | "
                    f"Status: {status_code} | Time: {elapsed_time:.2f}s | User: {user}"
                )
            
            # Log error responses
            if status_code >= 400:
                logger.error(
                    f"ERROR RESPONSE | {method} {path} | "
                    f"Status: {status_code} | Time: {elapsed_time:.2f}s | User: {user}"
                )
            else:
                logger.debug(
                    f"RESPONSE | {method} {path} | "
                    f"Status: {status_code} | Time: {elapsed_time:.2f}s"
                )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def mask_sensitive_data(self, data):
        """Mask sensitive fields in logged data."""
        masked_data = data.copy()
        for field in self.SENSITIVE_FIELDS:
            if field in masked_data:
                masked_data[field] = '***MASKED***'
        return masked_data


class UserActivityMiddleware(MiddlewareMixin):
    """
    Track and log user activities for audit trail.
    """
    
    # Track these HTTP methods as activities
    TRACKED_METHODS = ['POST', 'PUT', 'DELETE', 'PATCH']
    
    def process_request(self, request):
        """
        Record user activity.
        """
        if isinstance(request.user, AnonymousUser):
            return None
        
        if request.method in self.TRACKED_METHODS:
            activity_data = {
                'user_id': request.user.id,
                'username': request.user.username,
                'method': request.method,
                'path': request.path,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:255],
                'timestamp': time.time()
            }
            
            activity_logger.info(json.dumps(activity_data))
        
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


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Monitor and log application performance metrics.
    """
    
    # Define threshold for slow requests (in seconds)
    SLOW_REQUEST_THRESHOLD = 1.0
    
    def process_request(self, request):
        """Start timing the request."""
        request._start_time = time.time()
        request._db_queries_before = 0
        
        # Count database queries if DEBUG is enabled
        try:
            from django.db import connection
            from django.test.utils import CaptureQueriesContext
            request._capture_queries = CaptureQueriesContext(connection)
            request._capture_queries.__enter__()
        except:
            pass
        
        return None
    
    def process_response(self, request, response):
        """
        Log performance metrics.
        """
        if hasattr(request, '_start_time'):
            elapsed_time = time.time() - request._start_time
            path = request.path
            method = request.method
            status = response.status_code
            
            metrics = {
                'method': method,
                'path': path,
                'status': status,
                'response_time_ms': round(elapsed_time * 1000, 2)
            }
            
            # Add database query count if available
            try:
                if hasattr(request, '_capture_queries'):
                    request._capture_queries.__exit__(None, None, None)
                    from django.db import connection
                    metrics['database_queries'] = len(connection.queries)
            except:
                pass
            
            # Log slow requests
            if elapsed_time > self.SLOW_REQUEST_THRESHOLD:
                logger.warning(f"SLOW REQUEST | {json.dumps(metrics)}")
            else:
                logger.debug(f"PERFORMANCE | {json.dumps(metrics)}")
        
        return response
