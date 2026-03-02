"""
Middleware Usage Examples

Demonstra como usar e customizar os middlewares.
"""

# ============================================================================
# 1. USANDO LOGGING NOS VIEWS
# ============================================================================

from django.shortcuts import render
from django.views.generic import ListView
import logging

logger = logging.getLogger('helpdesk.middleware')
activity_logger = logging.getLogger('helpdesk.activity')


class TicketListView(ListView):
    model = 'Tickets'
    
    def get(self, request, *args, **kwargs):
        # Log activity
        logger.info(f"User {request.user.username} accessing ticket list")
        activity_logger.info(f"ACTION | User: {request.user.username} | Action: VIEW_TICKETS")
        
        return super().get(request, *args, **kwargs)


# ============================================================================
# 2. USANDO REQUEST USER INFO (Adicionado pelo Middleware)
# ============================================================================

def my_view(request):
    # IP adicionado pelo AuthenticationMiddleware
    client_ip = getattr(request, 'user_ip', 'Unknown')
    
    # User-Agent adicionado pelo AuthenticationMiddleware
    user_agent = getattr(request, 'user_agent', 'Unknown')
    
    # Papel do usuário adicionado pelo PermissionMiddleware
    user_role = getattr(request, 'user_role', 'unknown')
    
    print(f"Client: {client_ip}")
    print(f"Agent: {user_agent}")
    print(f"Role: {user_role}")
    
    return render(request, 'template.html')


# ============================================================================
# 3. CUSTOMIZAR RATE LIMITING
# ============================================================================

from tickets.middleware.config import MiddlewareConfig

# Aumentar limite para um usuário específico
MiddlewareConfig.SECURITY_CONFIG['rate_limit_authenticated'] = 200

# Ou diminuir para ser mais restritivo
MiddlewareConfig.SECURITY_CONFIG['rate_limit_anonymous'] = 10


# ============================================================================
# 4. ADICIONAR LOGGING PERSONALIZADO EM VIEWS
# ============================================================================

from django.http import JsonResponse
import json

def api_endpoint(request):
    user = request.user.username if request.user.is_authenticated else 'Anonymous'
    
    # Log da atividade
    activity_data = {
        'user': user,
        'action': 'API_CALL',
        'endpoint': request.path,
        'method': request.method,
        'ip': getattr(request, 'user_ip', 'Unknown'),
    }
    activity_logger.info(json.dumps(activity_data))
    
    return JsonResponse({'status': 'success'})


# ============================================================================
# 5. USAR UTILITY FUNCTIONS
# ============================================================================

from tickets.middleware.config import MiddlewareUtils

def smart_view(request):
    # Extrair IP
    client_ip = MiddlewareUtils.get_client_ip(request)
    
    # Identificador único do usuário
    user_id = MiddlewareUtils.get_user_identifier(request)
    
    # Verificar se é AJAX
    is_ajax = MiddlewareUtils.is_ajax_request(request)
    
    # Verificar se é API
    is_api = MiddlewareUtils.is_api_request(request)
    
    # Verificar se é mobile
    is_mobile = MiddlewareUtils.is_mobile_request(request)
    
    # Mascarar dados sensíveis
    data = {'password': '123456', 'email': 'user@example.com'}
    safe_data = MiddlewareUtils.mask_sensitive_data(data)
    # Result: {'password': '***MASKED***', 'email': 'user@example.com'}
    
    return JsonResponse({
        'ip': client_ip,
        'user_id': user_id,
        'is_ajax': is_ajax,
        'is_api': is_api,
        'is_mobile': is_mobile,
    })


# ============================================================================
# 6. ADICIONAR URLS PÚBLICAS
# ============================================================================

# Em tickets/middleware/config.py, adicione:
# PUBLIC_URLS = [
#     '/admin/login/',
#     '/login/',
#     '/register/',
#     '/api/public/status/',  # <-- Nova URL pública
#     '/health/ping/',
# ]


# ============================================================================
# 7. MONITORE PERFORMANCE EM VIEWS
# ============================================================================

from django.core.cache import cache
from django.db import connection

def complex_view(request):
    # Performance monitoring automático via PerformanceMonitoringMiddleware
    # Mas você pode adicionar logs customizados:
    
    logger = logging.getLogger('helpdesk.performance')
    
    import time
    start = time.time()
    
    # Sua lógica complexa aqui
    result = expensive_computation()
    
    elapsed = time.time() - start
    
    # Log se foi lento
    if elapsed > 1.0:
        logger.warning(
            f"Slow operation in complex_view: {elapsed:.2f}s | "
            f"DB Queries: {len(connection.queries)}"
        )
    
    return render(request, 'result.html', {'result': result})


# ============================================================================
# 8. AUDIT TRAIL - EXEMPLO DE RASTREAMENTO COMPLETO
# ============================================================================

def audit_logged_view(request):
    activity_logger = logging.getLogger('helpdesk.activity')
    
    # Antes da ação
    activity_logger.info(f"BEFORE | User: {request.user} | Action: DELETE_TICKET | ID: 123")
    
    # Executar ação
    ticket = delete_ticket(id=123)
    
    # Depois da ação
    activity_logger.info(f"AFTER | User: {request.user} | Action: DELETE_TICKET | Success: True")
    
    return JsonResponse({'status': 'deleted'})


# ============================================================================
# 9. ERROR HANDLING COM LOGGING
# ============================================================================

def error_handling_view(request):
    logger = logging.getLogger('helpdesk.errors')
    
    try:
        # Lógica que pode falhar
        result = risky_operation()
    except ValueError as e:
        logger.error(
            f"ValueError in error_handling_view: {str(e)} | "
            f"User: {request.user} | Data: {request.POST}"
        )
        return JsonResponse({'error': 'Invalid value'}, status=400)
    except Exception as e:
        logger.critical(
            f"Unexpected error: {str(e)} | "
            f"User: {request.user}",
            exc_info=True
        )
        return JsonResponse({'error': 'Internal error'}, status=500)
    
    return JsonResponse({'result': result})


# ============================================================================
# 10. INTEGRAÇÃO COM CACHE E RATE LIMITING
# ============================================================================

from django.core.cache import cache

def cached_endpoint(request):
    from tickets.middleware.security import RateLimitingMiddleware
    
    client_ip = RateLimitingMiddleware.get_client_ip(request)
    cache_key = f"endpoint_cache:{client_ip}"
    
    # Verificar cache
    cached_result = cache.get(cache_key)
    if cached_result:
        return JsonResponse(cached_result)
    
    # Computar resultado
    result = expensive_computation()
    
    # Guardar em cache por 5 minutos
    cache.set(cache_key, result, 300)
    
    return JsonResponse(result)


# ============================================================================
# 11. CUSTOM RESPONSE COM HEADERS DE SEGURANÇA
# ============================================================================

from django.http import HttpResponse

def secure_view(request):
    response = HttpResponse("Conteúdo seguro")
    
    # Headers são adicionados automaticamente por SecurityHeadersMiddleware
    # Mas você pode adicionar mais se necessário:
    response['X-Custom-Header'] = 'Custom Value'
    
    return response


# ============================================================================
# 12. TESTANDO RATE LIMITING
# ============================================================================

"""
Para testar rate limiting:

from django.test import Client

client = Client()

# Fazer 31+ requisições (limite anônimo é 30)
for i in range(35):
    response = client.get('/tickets/')
    if i < 30:
        assert response.status_code == 200
    else:
        assert response.status_code == 429  # Too Many Requests

# Verificar blacklist após violações repetidas
for i in range(36 * 4):  # 4 violações
    response = client.get('/tickets/')
    if i > 30 * 4:  # Após múltiplas violações
        assert response.status_code == 429
        # IP está blacklisteado por 1 hora
"""


# ============================================================================
# 13. VERIFICAR STATUS DE MIDDLEWARE
# ============================================================================

from tickets.middleware.config import MiddlewareConfig

def status_view(request):
    config = {
        'enabled_middleware': MiddlewareConfig.ENABLED_MIDDLEWARE,
        'rate_limits': MiddlewareConfig.SECURITY_CONFIG,
        'public_urls': MiddlewareConfig.PUBLIC_URLS,
    }
    
    return JsonResponse(config)


# ============================================================================
# 14. EXEMPLO DE LOG ESTRUTURADO
# ============================================================================

import json
from datetime import datetime

def structured_logging_view(request):
    activity_logger = logging.getLogger('helpdesk.activity')
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user_id': request.user.id if request.user.is_authenticated else None,
        'username': request.user.username if request.user.is_authenticated else None,
        'action': 'CREATE_TICKET',
        'resource_id': 123,
        'resource_type': 'Ticket',
        'ip_address': getattr(request, 'user_ip', 'Unknown'),
        'user_agent': getattr(request, 'user_agent', 'Unknown'),
        'status': 'success',
        'details': {
            'title': 'New Ticket',
            'description': 'Problem description',
        }
    }
    
    activity_logger.info(json.dumps(log_entry))
    
    return JsonResponse({'status': 'created'})


# ============================================================================
# DICAS IMPORTANTES
# ============================================================================

"""
1. LOGGING LEVELS:
   - DEBUG: Informações detalhadas para diagnóstico
   - INFO: Informações gerais (default em produção)
   - WARNING: Algo inesperado que merece atenção
   - ERROR: Um erro que não interrompe o programa
   - CRITICAL: Um erro grave que pode interromper

2. SENSIBLE FIELDS:
   Adicione a 'tickets/middleware/logging.py' se necessário:
   SENSITIVE_FIELDS = ['password', 'token', 'secret', 'api_key', 'credit_card', 'ssn']

3. PERFORMANCE:
   - Comprimir respostas > 512 bytes
   - Cache responses adequadamente
   - Monitore queries do banco

4. SEGURANÇA:
   - Rate limiting protege contra brute force
   - CSRF tokens validados automaticamente
   - Headers de segurança adicionados automaticamente

5. AUDITORIA:
   - Todos os eventos são registrados em logs/
   - Mantenha backups dos logs
   - Use ferramentas como ELK para análise

6. CUSTOM MIDDLEWARE:
   - Você pode criar seu próprio em tickets/middleware/
   - Use MiddlewareMixin como base
   - Registre em config.settings.MIDDLEWARE
   - Respeite a ordem de execução
"""
