"""
Middleware configuration and utilities.

Provides helper functions and configuration for all middleware.
"""

import logging
from django.conf import settings

logger = logging.getLogger('helpdesk.middleware')


class MiddlewareConfig:
    """
    Centralized configuration for all middleware.
    """
    
    # Enable/disable individual middleware
    ENABLED_MIDDLEWARE = {
        'authentication': True,
        'permission': True,
        'session_security': True,
        'request_logging': True,
        'user_activity': True,
        'performance_monitoring': True,
        'rate_limiting': True,
        'security_headers': True,
        'request_validation': True,
        'cors': True,
        'error_handling': True,
        'http404': True,
        'http500': True,
        'validation_error': True,
        'response_formatting': True,
        'compression': True,
        'cache_control': True,
    }
    
    # Logging configuration
    LOG_LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }
    
    # Public URLs that don't require authentication
    PUBLIC_URLS = [
        '/admin/login/',
        '/login/',
        '/register/',
        '/password-reset/',
        '/password-reset/done/',
        '/password-reset/confirm/',
        '/password-reset/complete/',
        '/static/',
        '/media/',
        '/api/public/',
        '/health/',
        '/ping/',
    ]
    
    # Security settings
    SECURITY_CONFIG = {
        'rate_limit_anonymous': 30,
        'rate_limit_authenticated': 100,
        'rate_limit_admin': 500,
        'rate_limit_window': 60,  # seconds
        'blacklist_duration': 3600,  # seconds
        'session_timeout': 3600,  # seconds
        'inactivity_timeout': 1800,  # seconds
        'max_request_body': 10 * 1024 * 1024,  # 10 MB
    }
    
    # Performance settings
    PERFORMANCE_CONFIG = {
        'slow_request_threshold': 1.0,  # seconds
        'log_all_requests': False,
        'profile_requests': False,
    }
    
    # Compression settings
    COMPRESSION_CONFIG = {
        'enabled': True,
        'min_size': 512,  # bytes
        'compression_level': 6,
    }
    
    # Cache settings
    CACHE_CONFIG = {
        'static_cache_age': 31536000,  # 1 year
        'html_cache_age': 3600,  # 1 hour
        'json_cache_age': 300,  # 5 minutes
    }
    
    @classmethod
    def is_middleware_enabled(cls, middleware_name):
        """Check if a middleware is enabled."""
        return cls.ENABLED_MIDDLEWARE.get(middleware_name, False)
    
    @classmethod
    def get_public_urls(cls):
        """Get list of public URLs."""
        return cls.PUBLIC_URLS
    
    @classmethod
    def get_security_config(cls, key, default=None):
        """Get security configuration value."""
        return cls.SECURITY_CONFIG.get(key, default)
    
    @classmethod
    def get_performance_config(cls, key, default=None):
        """Get performance configuration value."""
        return cls.PERFORMANCE_CONFIG.get(key, default)
    
    @classmethod
    def log_config(cls):
        """Log current middleware configuration."""
        logger.info("=== Middleware Configuration ===")
        logger.info(f"Debug Mode: {settings.DEBUG}")
        logger.info(f"Enabled Middleware: {[k for k, v in cls.ENABLED_MIDDLEWARE.items() if v]}")
        logger.info(f"Rate Limits: Anon={cls.SECURITY_CONFIG['rate_limit_anonymous']}, "
                   f"Auth={cls.SECURITY_CONFIG['rate_limit_authenticated']}, "
                   f"Admin={cls.SECURITY_CONFIG['rate_limit_admin']}")
        logger.info("=== ===========================")


class MiddlewareUtils:
    """
    Utility functions for middleware.
    """
    
    @staticmethod
    def get_client_ip(request):
        """
        Extract client IP address from request.
        
        Handles:
        - X-Forwarded-For header (for proxies)
        - REMOTE_ADDR (direct connection)
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    @staticmethod
    def get_user_identifier(request):
        """
        Get unique identifier for the user/client.
        """
        if request.user.is_authenticated:
            return f"user_{request.user.id}"
        else:
            return f"ip_{MiddlewareUtils.get_client_ip(request)}"
    
    @staticmethod
    def is_ajax_request(request):
        """
        Check if request is AJAX.
        """
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    
    @staticmethod
    def is_api_request(request):
        """
        Check if request is API request.
        """
        return request.path.startswith('/api/') or \
               'application/json' in request.META.get('HTTP_ACCEPT', '')
    
    @staticmethod
    def get_user_agent(request):
        """
        Get user agent string.
        """
        return request.META.get('HTTP_USER_AGENT', 'Unknown')[:255]
    
    @staticmethod
    def get_referrer(request):
        """
        Get HTTP referrer.
        """
        return request.META.get('HTTP_REFERER', '')
    
    @staticmethod
    def is_mobile_request(request):
        """
        Check if request is from mobile device.
        """
        user_agent = MiddlewareUtils.get_user_agent(request).lower()
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'windows phone']
        return any(keyword in user_agent for keyword in mobile_keywords)
    
    @staticmethod
    def mask_sensitive_data(data, sensitive_fields=None):
        """
        Mask sensitive fields in data dict.
        """
        if sensitive_fields is None:
            sensitive_fields = ['password', 'token', 'secret', 'api_key', 'credit_card']
        
        masked_data = data.copy() if isinstance(data, dict) else dict(data)
        for field in sensitive_fields:
            if field in masked_data:
                masked_data[field] = '***MASKED***'
        return masked_data
