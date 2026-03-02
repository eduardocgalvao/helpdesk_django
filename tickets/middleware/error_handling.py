"""
Error Handling Middleware

Handles:
- Exception catching and logging
- Graceful error responses
- 404 and 500 error handling
- Error reporting
"""

import logging
import traceback
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import condition
from django.conf import settings

logger = logging.getLogger('helpdesk.errors')


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Catch and handle exceptions gracefully.
    """
    
    def process_exception(self, request, exception):
        """
        Handle exceptions that occur during view processing.
        """
        exc_type = type(exception).__name__
        exc_message = str(exception)
        ip = self.get_client_ip(request)
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        
        # Log full traceback
        logger.error(
            f"Exception in view: {exc_type} - {exc_message}\n"
            f"User: {user} | IP: {ip} | Path: {request.path}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        
        # Return appropriate response based on exception type
        if settings.DEBUG:
            # In debug mode, let Django's default error handling take over
            return None
        else:
            # In production, return generic error response
            return JsonResponse(
                {
                    'error': 'An error occurred processing your request',
                    'type': exc_type if settings.DEBUG else 'Error',
                },
                status=500
            )
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class Http404Middleware(MiddlewareMixin):
    """
    Handle 404 Not Found errors gracefully.
    """
    
    def process_response(self, request, response):
        """
        Check for 404 responses and log them.
        """
        if response.status_code == 404:
            user = request.user.username if request.user.is_authenticated else 'Anonymous'
            ip = self.get_client_ip(request)
            
            logger.warning(
                f"404 Not Found | User: {user} | IP: {ip} | "
                f"Path: {request.path} | Referrer: {request.META.get('HTTP_REFERER', 'None')}"
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


class Http500Middleware(MiddlewareMixin):
    """
    Handle 500 Internal Server Error responses.
    """
    
    def process_response(self, request, response):
        """
        Log 500 errors.
        """
        if response.status_code == 500:
            user = request.user.username if request.user.is_authenticated else 'Anonymous'
            ip = self.get_client_ip(request)
            
            logger.critical(
                f"500 Internal Server Error | User: {user} | IP: {ip} | "
                f"Path: {request.path} | Method: {request.method}"
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


class ValidationErrorMiddleware(MiddlewareMixin):
    """
    Handle validation errors and return appropriate responses.
    """
    
    def process_response(self, request, response):
        """
        Check for validation-related responses.
        """
        if response.status_code == 400:
            user = request.user.username if request.user.is_authenticated else 'Anonymous'
            ip = self.get_client_ip(request)
            
            logger.warning(
                f"400 Bad Request | User: {user} | IP: {ip} | "
                f"Path: {request.path} | Method: {request.method}"
            )
        
        elif response.status_code == 403:
            user = request.user.username if request.user.is_authenticated else 'Anonymous'
            ip = self.get_client_ip(request)
            
            logger.warning(
                f"403 Forbidden | User: {user} | IP: {ip} | "
                f"Path: {request.path}"
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
