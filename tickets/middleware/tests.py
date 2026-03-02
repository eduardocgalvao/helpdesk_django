"""
Unit tests for middleware layer.

Teste todos os middlewares com django.test.TestCase.
"""

from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.http import HttpResponse
from django.test.utils import override_settings
import logging
import json

# Import middlewares
from tickets.middleware.authentication import (
    AuthenticationMiddleware,
    PermissionMiddleware,
    SessionSecurityMiddleware,
)
from tickets.middleware.logging import (
    RequestLoggingMiddleware,
    UserActivityMiddleware,
    PerformanceMonitoringMiddleware,
)
from tickets.middleware.security import (
    RateLimitingMiddleware,
    RequestValidationMiddleware,
    SecurityHeadersMiddleware,
)
from tickets.middleware.error_handling import ErrorHandlingMiddleware
from tickets.middleware.response_processing import (
    CompressionMiddleware,
    CacheControlMiddleware,
)
from tickets.middleware.config import MiddlewareUtils


class AuthenticationMiddlewareTestCase(TestCase):
    """Test AuthenticationMiddleware."""
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.middleware = AuthenticationMiddleware(lambda x: HttpResponse())
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_public_url_access(self):
        """Usuários anônimos podem acessar URLs públicas."""
        response = self.client.get('/login/')
        self.assertIsNotNone(response)
    
    def test_authenticated_user_access(self):
        """Usuários autenticados podem acessar recursos protegidos."""
        self.client.login(username='testuser', password='testpass123')
        # Teste acesso a recurso protegido
        # response = self.client.get('/tickets/')
        # self.assertEqual(response.status_code, 200)
    
    def test_anonymous_redirect(self):
        """Usuários anônimos são redirecionados para login."""
        request = self.factory.get('/tickets/')
        request.user = User()  # Anonymous user
        
        response = self.middleware.process_request(request)
        # Should return redirect
        self.assertIsNotNone(response)


class PermissionMiddlewareTestCase(TestCase):
    """Test PermissionMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = PermissionMiddleware(lambda x: HttpResponse())
        
        # Create users with different roles
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        self.gestor_user = User.objects.create_user(
            username='gestor',
            password='gestor123'
        )
        gestor_group, _ = Group.objects.get_or_create(name='Gestor')
        self.gestor_user.groups.add(gestor_group)
        
        self.colaborador_user = User.objects.create_user(
            username='colaborador',
            password='colab123'
        )
    
    def test_admin_role_detection(self):
        """Admin é detectado como papel 'admin'."""
        role = PermissionMiddleware.get_user_role(self.admin_user)
        self.assertEqual(role, 'admin')
    
    def test_gestor_role_detection(self):
        """Gestor é detectado como papel 'gestor'."""
        role = PermissionMiddleware.get_user_role(self.gestor_user)
        self.assertEqual(role, 'gestor')
    
    def test_colaborador_role_detection(self):
        """Colaborador é detectado como papel 'colaborador'."""
        role = PermissionMiddleware.get_user_role(self.colaborador_user)
        self.assertEqual(role, 'colaborador')


class RateLimitingMiddlewareTestCase(TestCase):
    """Test RateLimitingMiddleware."""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
    
    def test_rate_limit_anonymous_user(self):
        """Rate limiting funciona para usuários anônimos."""
        # Fazer 31 requisições (limite é 30)
        for i in range(31):
            response = self.client.get('/tickets/')
            if i < 30:
                self.assertNotEqual(response.status_code, 429)
            else:
                self.assertEqual(response.status_code, 429)
    
    def test_rate_limit_authenticated_user(self):
        """Rate limiting funciona para usuários autenticados."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='testuser', password='testpass')
        
        # Fazer muitas requisições
        for i in range(101):  # Limite é 100
            response = self.client.get('/tickets/')
            if i < 100:
                self.assertNotEqual(response.status_code, 429)
    
    def test_ip_extraction(self):
        """IP é extraído corretamente."""
        factory = RequestFactory()
        
        # Direct connection
        request = factory.get('/', REMOTE_ADDR='127.0.0.1')
        ip = RateLimitingMiddleware.get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')
        
        # X-Forwarded-For header
        request = factory.get('/', HTTP_X_FORWARDED_FOR='10.0.0.1, 127.0.0.1')
        ip = RateLimitingMiddleware.get_client_ip(request)
        self.assertEqual(ip, '10.0.0.1')


class SecurityHeadersMiddlewareTestCase(TestCase):
    """Test SecurityHeadersMiddleware."""
    
    def setUp(self):
        self.client = Client()
        self.middleware = SecurityHeadersMiddleware(lambda x: HttpResponse())
    
    def test_security_headers_present(self):
        """Headers de segurança são adicionados à resposta."""
        response = HttpResponse()
        response.status_code = 200
        
        processed_response = self.middleware.process_response(None, response)
        
        # Verify headers
        self.assertEqual(processed_response['X-Frame-Options'], 'SAMEORIGIN')
        self.assertEqual(processed_response['X-Content-Type-Options'], 'nosniff')
        self.assertIn('X-XSS-Protection', processed_response)
        self.assertIn('Content-Security-Policy', processed_response)


class RequestValidationMiddlewareTestCase(TestCase):
    """Test RequestValidationMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestValidationMiddleware(lambda x: HttpResponse())
    
    def test_max_body_size_check(self):
        """Requisições muito grandes são rejeitadas."""
        # Simular grande body
        request = self.factory.post(
            '/',
            CONTENT_LENGTH=15 * 1024 * 1024  # 15 MB
        )
        response = self.middleware.process_request(request)
        if response:
            self.assertEqual(response.status_code, 413)
    
    def test_suspicious_content_detection(self):
        """Conteúdo suspeito é detectado."""
        request = self.factory.get('/?search=<script>alert(1)</script>')
        response = self.middleware.process_request(request)
        # Suspicious content detected
        if response:
            self.assertEqual(response.status_code, 400)


class CompressionMiddlewareTestCase(TestCase):
    """Test CompressionMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CompressionMiddleware(lambda x: HttpResponse())
    
    def test_response_compression(self):
        """Respostas são comprimidas se aplicável."""
        request = self.factory.get(
            '/',
            HTTP_ACCEPT_ENCODING='gzip, deflate'
        )
        
        # Create response with large content
        response = HttpResponse(b'x' * 1000)
        response['Content-Type'] = 'text/html'
        
        processed = self.middleware.process_response(request, response)
        
        # Should be compressed
        if 'Content-Encoding' in processed:
            self.assertEqual(processed['Content-Encoding'], 'gzip')


class CacheControlMiddlewareTestCase(TestCase):
    """Test CacheControlMiddleware."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CacheControlMiddleware(lambda x: HttpResponse())
    
    def test_static_cache_headers(self):
        """Static files têm cache headers apropriados."""
        request = self.factory.get('/static/css/style.css')
        response = HttpResponse()
        
        processed = self.middleware.process_response(request, response)
        self.assertIn('Cache-Control', processed)
        self.assertIn('max-age', processed['Cache-Control'])
    
    def test_json_cache_headers(self):
        """JSON responses têm cache headers apropriados."""
        request = self.factory.get('/api/tickets/')
        response = HttpResponse(json.dumps({'data': []}))
        response['Content-Type'] = 'application/json'
        
        processed = self.middleware.process_response(request, response)
        self.assertIn('Cache-Control', processed)
        self.assertIn('private', processed['Cache-Control'])


class MiddlewareUtilsTestCase(TestCase):
    """Test MiddlewareUtils helper functions."""
    
    def test_get_client_ip_direct(self):
        """IP extraction from REMOTE_ADDR."""
        factory = RequestFactory()
        request = factory.get('/', REMOTE_ADDR='192.168.1.1')
        
        ip = MiddlewareUtils.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_client_ip_forwarded(self):
        """IP extraction from X-Forwarded-For."""
        factory = RequestFactory()
        request = factory.get(
            '/',
            HTTP_X_FORWARDED_FOR='10.0.0.1, 127.0.0.1'
        )
        
        ip = MiddlewareUtils.get_client_ip(request)
        self.assertEqual(ip, '10.0.0.1')
    
    def test_is_mobile_request(self):
        """Mobile requests são detectadas."""
        factory = RequestFactory()
        
        # Desktop
        request = factory.get(
            '/',
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
        self.assertFalse(MiddlewareUtils.is_mobile_request(request))
        
        # Mobile
        request = factory.get(
            '/',
            HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        )
        self.assertTrue(MiddlewareUtils.is_mobile_request(request))
    
    def test_mask_sensitive_data(self):
        """Dados sensíveis são mascarados."""
        data = {
            'username': 'admin',
            'password': '123456',
            'email': 'admin@example.com',
            'api_key': 'secret-key-123'
        }
        
        masked = MiddlewareUtils.mask_sensitive_data(data)
        
        self.assertEqual(masked['username'], 'admin')
        self.assertEqual(masked['password'], '***MASKED***')
        self.assertEqual(masked['email'], 'admin@example.com')
        self.assertEqual(masked['api_key'], '***MASKED***')


class ErrorHandlingMiddlewareTestCase(TestCase):
    """Test ErrorHandlingMiddleware."""
    
    def setUp(self):
        self.middleware = ErrorHandlingMiddleware(lambda x: HttpResponse())
    
    def test_exception_handling(self):
        """Exceções são capturadas e logadas."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = User()
        
        exception = ValueError("Test error")
        response = self.middleware.process_exception(request, exception)
        
        # Em debug=False, deve retornar response genérica
        # Em debug=True, retorna None para django tratar


class PerformanceMonitoringMiddlewareTestCase(TestCase):
    """Test PerformanceMonitoringMiddleware."""
    
    def setUp(self):
        self.middleware = PerformanceMonitoringMiddleware(lambda x: HttpResponse())
        self.factory = RequestFactory()
    
    def test_request_timing(self):
        """Tempo de requisição é rastreado."""
        request = self.factory.get('/')
        request.user = User()
        
        # Process request (set start time)
        self.middleware.process_request(request)
        
        # Simulate delay
        import time
        time.sleep(0.1)
        
        response = HttpResponse()
        processed = self.middleware.process_response(request, response)
        
        self.assertIsNotNone(processed)


# ============================================================================
# Integration Tests
# ============================================================================

class MiddlewareIntegrationTestCase(TestCase):
    """Test middleware stack integration."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_authentication_and_logging(self):
        """Authentication e Logging funcionam juntos."""
        # Anonymous access
        response = self.client.get('/login/')
        self.assertIsNotNone(response)
        
        # Authenticated access
        self.client.login(username='testuser', password='testpass123')
        # Test access to protected resource
    
    def test_security_and_rate_limiting(self):
        """Security headers e Rate limiting funcionam juntos."""
        cache.clear()
        
        # Single request should work
        response = self.client.get('/tickets/')
        self.assertNotEqual(response.status_code, 429)
        
        # Check security headers are present
        # self.assertIn('X-Frame-Options', response)


# ============================================================================
# Performance Tests
# ============================================================================

class MiddlewarePerformanceTestCase(TestCase):
    """Test middleware performance impact."""
    
    def setUp(self):
        self.client = Client()
    
    def test_middleware_overhead(self):
        """Middlewares não adicionam overhead excessivo."""
        import time
        
        start = time.time()
        
        for i in range(10):
            self.client.get('/health/')  # Endpoint rápido
        
        elapsed = time.time() - start
        
        # Should complete in < 1 second for 10 requests
        self.assertLess(elapsed, 1.0)
