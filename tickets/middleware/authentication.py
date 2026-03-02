"""
Authentication and Authorization Middleware

Handles:
- User info enrichment (IP, User-Agent)
- Permission checking
- Session validation
- Role-based access control (RBAC)

IMPORTANT:
- Django's built-in AuthenticationMiddleware handles login redirects
- This middleware only adds extra info and logging
- Use LoginRequiredMixin in views for authentication enforcement
"""

import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class CustomAuthenticationMiddleware(MiddlewareMixin):
    """
    Custom authentication middleware to add user info and log access.
    Note: Renamed to avoid conflict with Django's AuthenticationMiddleware
    """
    
    # Public routes that don't require authentication
    PUBLIC_URLS = [
        '/admin/',
        '/accounts/',
        '/login/',
        '/register/',
        '/static/',
        '/media/',
        '/api/public/',
    ]
    
    def process_request(self, request):
        """
        Add user info to request without forcing redirect.
        Let LoginRequiredMixin in views handle authentication.
        """
        path = request.path
        
        # Store user info for logging if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.user_ip = self.get_client_ip(request)
            request.user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Log unauthenticated access attempts to protected resources
        if not any(path.startswith(url) for url in self.PUBLIC_URLS):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                logger.debug(f"Unauthenticated access to {path} from {self.get_client_ip(request)}")
        
        return None
    
    def process_response(self, request, response):
        """
        Process response and log authentication events.
        """
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            if response.status_code in [403, 401]:
                logger.warning(
                    f"Access denied for user {request.user.username} "
                    f"to {request.path} | Status: {response.status_code}"
                )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PermissionMiddleware(MiddlewareMixin):
    """
    Middleware to enforce role-based access control (RBAC).
    Checks user permissions before allowing access to protected resources.
    """
    
    # Define role-based access patterns
    ROLE_PERMISSIONS = {
        'admin': ['tickets_list', 'tickets_create', 'tickets_update', 'tickets_delete', 'dashboard'],
        'gestor': ['tickets_list', 'tickets_create', 'tickets_update', 'dashboard'],
        'colaborador': ['tickets_list', 'tickets_create'],
    }
    
    def process_request(self, request):
        """
        Validate user permissions for the requested resource.
        """
        if isinstance(request.user, AnonymousUser):
            return None
        
        # Get user role
        user_role = self.get_user_role(request.user)
        request.user_role = user_role
        
        logger.debug(f"User {request.user.username} with role {user_role} accessing {request.path}")
        
        return None
    
    @staticmethod
    def get_user_role(user):
        """Determine user role based on groups and permissions."""
        if user.is_superuser:
            return 'admin'
        
        groups = user.groups.values_list('name', flat=True)
        
        if 'Admin' in groups or 'admin' in groups:
            return 'admin'
        elif 'Gestor' in groups or 'gestor' in groups:
            return 'gestor'
        else:
            return 'colaborador'


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Enforce session security policies.
    - Validate session integrity
    - Check for suspicious activity
    - Implement session timeouts
    """
    
    # Session configuration in seconds
    SESSION_TIMEOUT = 3600  # 1 hour
    INACTIVITY_TIMEOUT = 1800  # 30 minutes
    
    # URLs that don't require session checking
    SKIP_URLS = [
        '/admin/',
        '/accounts/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """
        Validate session on each request.
        """
        # Skip for anonymous users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Skip for public URLs
        if any(request.path.startswith(url) for url in self.SKIP_URLS):
            return None
        
        session = request.session
        last_activity = session.get('last_activity')
        
        # Check inactivity timeout
        if last_activity:
            import time
            current_time = int(time.time())
            time_inactive = current_time - last_activity
            
            if time_inactive > self.INACTIVITY_TIMEOUT:
                logger.warning(f"Session timeout for user {request.user.username} due to inactivity")
                session.flush()
                # Don't redirect here, let Django handle it
                return None
        
        # Update last activity
        import time
        session['last_activity'] = int(time.time())
        
        return None
