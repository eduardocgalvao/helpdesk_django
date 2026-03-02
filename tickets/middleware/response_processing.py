"""
Response Processing Middleware

Handles:
- Response compression
- Response formatting
- Content negotiation
- Response modification
"""

import logging
import gzip
import io
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import force_bytes

logger = logging.getLogger('helpdesk.response')


class ResponseFormattingMiddleware(MiddlewareMixin):
    """
    Format responses consistently across the application.
    """
    
    # Content types that should be formatted
    JSON_TYPES = [
        'application/json',
        'application/ld+json',
    ]
    
    def process_response(self, request, response):
        """
        Format response based on content type.
        """
        content_type = response.get('Content-Type', '').split(';')[0]
        
        # Add content length if not present
        if 'Content-Length' not in response:
            try:
                response['Content-Length'] = len(response.content)
            except:
                pass
        
        # Add custom headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        
        return response


class CompressionMiddleware(MiddlewareMixin):
    """
    Compress responses for faster transfer (GZIP).
    
    Only compress responses:
    - Larger than 512 bytes
    - Not already compressed
    - With compressible content types
    """
    
    MIN_SIZE = 512
    
    COMPRESSIBLE_TYPES = [
        'text/html',
        'text/plain',
        'text/css',
        'application/javascript',
        'application/json',
        'application/xml',
        'application/ld+json',
        'text/xml',
        'image/svg+xml',
    ]
    
    def process_response(self, request, response):
        """
        Compress response if applicable.
        """
        # Check if client supports gzip
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        if 'gzip' not in accept_encoding:
            return response
        
        # Check if response is already compressed
        if response.get('Content-Encoding'):
            return response
        
        # Check content type
        content_type = response.get('Content-Type', '').split(';')[0]
        if not any(ct in content_type for ct in self.COMPRESSIBLE_TYPES):
            return response
        
        # Check response size
        content_length = len(response.content)
        if content_length < self.MIN_SIZE:
            return response
        
        try:
            # Compress content
            gzip_buffer = io.BytesIO()
            gzip_file = gzip.GzipFile(
                mode='wb',
                fileobj=gzip_buffer,
                compresslevel=6
            )
            gzip_file.write(response.content)
            gzip_file.close()
            
            compressed_content = gzip_buffer.getvalue()
            
            # Update response
            response.content = compressed_content
            response['Content-Encoding'] = 'gzip'
            response['Content-Length'] = len(compressed_content)
            
            logger.debug(
                f"Compressed response from {content_length} to {len(compressed_content)} bytes "
                f"for {request.path}"
            )
        
        except Exception as e:
            logger.error(f"Error compressing response: {str(e)}")
        
        return response


class CacheControlMiddleware(MiddlewareMixin):
    """
    Set appropriate cache control headers based on response type.
    """
    
    # Cache configuration
    CACHE_PERIODS = {
        'static': 31536000,      # 1 year
        'html': 3600,            # 1 hour
        'json': 300,             # 5 minutes
        'default': 0,            # No cache
    }
    
    def process_response(self, request, response):
        """
        Set cache headers based on response type.
        """
        path = request.path
        content_type = response.get('Content-Type', '').split(';')[0]
        
        # Static files
        if path.startswith('/static/') or path.startswith('/media/'):
            max_age = self.CACHE_PERIODS['static']
            response['Cache-Control'] = f'public, max-age={max_age}'
        
        # JSON responses
        elif 'application/json' in content_type:
            max_age = self.CACHE_PERIODS['json']
            response['Cache-Control'] = f'private, max-age={max_age}'
        
        # HTML responses
        elif 'text/html' in content_type:
            max_age = self.CACHE_PERIODS['html']
            response['Cache-Control'] = f'private, max-age={max_age}'
        
        # No cache by default for authenticated users
        else:
            if request.user.is_authenticated:
                response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
            else:
                response['Cache-Control'] = 'public, max-age=0'
        
        return response


class XContentTypeOptionsMiddleware(MiddlewareMixin):
    """
    Prevent content type sniffing.
    """
    
    def process_response(self, request, response):
        """
        Add X-Content-Type-Options header.
        """
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class ContentLengthMiddleware(MiddlewareMixin):
    """
    Ensure Content-Length header is set for all responses.
    """
    
    def process_response(self, request, response):
        """
        Set Content-Length if not already set.
        """
        if 'Content-Length' not in response and response.streaming is False:
            try:
                response['Content-Length'] = len(response.content)
            except:
                pass
        
        return response
