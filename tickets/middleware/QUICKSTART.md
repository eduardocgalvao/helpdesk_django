"""
QUICK START - Middleware Layer

Guia rápido para começar a usar a camada de middleware.
"""

# ============================================================================
# STEP 1: VERIFICAR INSTALAÇÃO
# ============================================================================

"""
1. Verifique se os arquivos foram criados em:
   tickets/middleware/
   ├── __init__.py
   ├── authentication.py
   ├── logging.py
   ├── security.py
   ├── error_handling.py
   ├── response_processing.py
   ├── config.py
   ├── logging_config.py
   ├── tests.py
   ├── examples.py
   ├── README.md
   └── ARCHITECTURE.md

2. Verifique se MIDDLEWARE foi atualizado em config/settings.py
"""


# ============================================================================
# STEP 2: CRIAR DIRETÓRIO DE LOGS
# ============================================================================

import os
from pathlib import Path

# Executar no shell Django ou gerenciar.py shell
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

print(f"✓ Log directory created at: {LOGS_DIR}")


# ============================================================================
# STEP 3: TESTAR MIDDLEWARE
# ============================================================================

"""
Executar testes para verificar funcionamento:

# Terminal
python manage.py test tickets.middleware.tests

# Saída esperada:
# ............
# Ran 12 tests in 0.234s
# OK
"""


# ============================================================================
# STEP 4: VERIFICAR LOGS
# ============================================================================

"""
Após executar a aplicação, verifique os logs:

ls -la logs/
├── middleware.log      (Operações gerais)
├── activity.log        (Auditoria)
├── security.log        (Eventos de segurança)
├── errors.log          (Erros)
└── performance.log     (Performance)

# Ver últimas linhas do log
tail -f logs/middleware.log
"""


# ============================================================================
# STEP 5: USAR NO CÓDIGO
# ============================================================================

# Em seus views, importe loggers:
import logging
from tickets.middleware.config import MiddlewareUtils

logger = logging.getLogger('helpdesk.middleware')
activity_logger = logging.getLogger('helpdesk.activity')

def my_view(request):
    # Log uma ação
    user_id = request.user.id if request.user.is_authenticated else None
    client_ip = MiddlewareUtils.get_client_ip(request)
    
    logger.info(f"User {user_id} from {client_ip} accessing resource")
    activity_logger.info(f"ACTION | User: {request.user.username} | IP: {client_ip}")
    
    # Seu código aqui
    return render(request, 'template.html')


# ============================================================================
# STEP 6: CONFIGURAR CUSTOMIZAÇÕES
# ============================================================================

# Editar tickets/middleware/config.py para customizar:

# 1. Aumentar rate limits
SECURITY_CONFIG = {
    'rate_limit_anonymous': 50,      # De 30
    'rate_limit_authenticated': 200,  # De 100
    'rate_limit_admin': 1000,         # De 500
}

# 2. Adicionar URLs públicas
PUBLIC_URLS = [
    '/admin/login/',
    '/login/',
    '/register/',
    '/api/public/health/',  # <- Sua URL
]

# 3. Desabilitar middlewares específicos (se necessário)
ENABLED_MIDDLEWARE = {
    'rate_limiting': False,  # Desabilitar se quiser
    # ... resto ...
}


# ============================================================================
# STEP 7: MONITORAR PERFORMANCE
# ============================================================================

"""
Para monitorar performance, verifique logs/performance.log:

[2024-01-15 10:30:45] WARNING - SLOW REQUEST | {
  "method": "GET",
  "path": "/tickets/list/",
  "status": 200,
  "response_time_ms": 1250.34,
  "database_queries": 15
}

Ações:
1. Se response_time > 1000ms: Otimizar view
2. Se database_queries > 10: Usar select_related/prefetch_related
3. Se compressão não ativa: Verificar CompressionMiddleware
"""


# ============================================================================
# STEP 8: VERIFICAR SEGURANÇA
# ============================================================================

"""
1. Headers de Segurança:
   
   GET /tickets/
   
   Response headers esperados:
   ✓ X-Frame-Options: SAMEORIGIN
   ✓ X-Content-Type-Options: nosniff
   ✓ X-XSS-Protection: 1; mode=block
   ✓ Content-Security-Policy: default-src 'self'
   ✓ Referrer-Policy: strict-origin-when-cross-origin

2. Rate Limiting:
   
   Fazer > 30 requisições de IP anônimo deve retornar 429

3. Authentication:
   
   Acessar /tickets/ sem login deve redirecionar para /login/

4. Permissões:
   
   Usuário sem permissão deve receber 403 Forbidden
"""


# ============================================================================
# STEP 9: USAR LOGS PARA AUDITORIA
# ============================================================================

"""
Exemplo de uso de logs para auditoria:

1. Rastrear ações de usuário:
   grep "usuario_id=5" logs/activity.log

2. Encontrar tentativas de ataque:
   grep "Rate limit exceeded" logs/security.log

3. Debugar erro específico:
   grep "500\|ERROR" logs/errors.log

4. Analisar performance:
   grep "SLOW REQUEST" logs/performance.log
   
5. Exportar para análise:
   cat logs/activity.log | python -m json.tool > audit_report.json
"""


# ============================================================================
# STEP 10: INTEGRAR COM FERRAMENTAS EXTERNAS
# ============================================================================

"""
Exemplo: Enviar logs para Sentry (error tracking)

# requirements.txt
sentry-sdk

# Em settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://seu-dsn@sentry.io/projeto-id",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False
)

Exemplo: Usar ELK Stack para logs centralizados

# requirements.txt
python-logstash-async

# Em logging_config.py adicione:
from logstash_async.handler import AsynchronousLogstashHandler

handler = AsynchronousLogstashHandler(
    'logstash-host',
    5959,
    database_path='logstash.db'
)
logger.addHandler(handler)
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Problema: "ModuleNotFoundError: No module named 'tickets.middleware'"

Solução:
1. Verificar se __init__.py existe em tickets/middleware/
2. Executar: python manage.py check
3. Limpar cache Python: find . -type d -name __pycache__ -exec rm -r {} +

---

Problema: Rate limiting muito agressivo

Solução:
1. Editar config.py e aumentar RATE_LIMITS
2. Verificar se cache está funcionando: python manage.py shell
   >>> from django.core.cache import cache
   >>> cache.set('test', 'value')
   >>> cache.get('test')
   'value'

---

Problema: Logs não aparecem

Solução:
1. Verificar se logs/ existe: ls -la logs/
2. Verificar permissões: chmod 755 logs/
3. Verificar DEBUG mode:
   >>> from django.conf import settings
   >>> settings.DEBUG
4. Forçar logging em settings.py:
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'handlers': {
           'console': {
               'class': 'logging.StreamHandler',
           },
       },
       'root': {
           'handlers': ['console'],
           'level': 'DEBUG',
       },
   }

---

Problema: CORS bloqueando requisições

Solução:
1. Adicionar origem em security.py:
   ALLOWED_ORIGINS = ['http://seu-frontend.com']
2. Verificar headers: curl -H "Origin: http://seu-frontend.com" http://localhost:8000/

---

Problema: Headers de segurança não aparecendo

Solução:
1. Verificar se SecurityHeadersMiddleware está registrado
2. Testar com: curl -i http://localhost:8000/tickets/
3. Verificar se response não está removendo headers
"""


# ============================================================================
# CHECKLIST DE DEPLOYMENT
# ============================================================================

"""
Pre-Production Checklist:

□ Verificar se todos os arquivos de middleware foram criados
□ Executar testes: python manage.py test tickets.middleware
□ Criar diretório logs/: mkdir logs/
□ Configurar permissões: chmod 755 logs/
□ Testar rate limiting
□ Testar autenticação
□ Testar headers de segurança
□ Configurar CSRF_COOKIE_SECURE = True (HTTPS)
□ Configurar SESSION_COOKIE_SECURE = True (HTTPS)
□ Revisionar limites de rate limiting
□ Revisar ALLOWED_HOSTS
□ Revisar ALLOWED_ORIGINS
□ Configurar logging rotation
□ Testar com dados reais
□ Monitorar logs em produção
□ Configurar alertas para erros críticos
□ Integrar com Sentry/APM tool
□ Fazer backup de logs regularmente
□ Documentar customizações feitas

Production Checklist:

□ Ativar HTTPS (DEBUG=False)
□ Configurar email para alertas
□ Monitorar logs/security.log
□ Monitorar logs/errors.log
□ Revisar logs/activity.log diariamente
□ Otimizar rate limits baseado em padrões
□ Arquivar logs antigos
□ Manter backups de segurança
□ Testar disaster recovery
"""


# ============================================================================
# EXEMPLO DE USO EM PRODUÇÃO
# ============================================================================

# logging_production.py - Configuração para produção

import logging
import os

# Configurar logger com file rotation
def setup_production_logging():
    from logging.handlers import RotatingFileHandler
    
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Logger de segurança
    security_logger = logging.getLogger('helpdesk.security')
    security_logger.setLevel(logging.WARNING)
    
    handler = RotatingFileHandler(
        os.path.join(log_dir, 'security.log'),
        maxBytes=50 * 1024 * 1024,  # 50 MB
        backupCount=10  # Manter 10 arquivos
    )
    
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)
    
    return security_logger


# Use em settings.py:
# from .logging_production import setup_production_logging
# if not DEBUG:
#     setup_production_logging()


# ============================================================================
# COMANDOS ÚTEIS
# ============================================================================

"""
# Executar testes
python manage.py test tickets.middleware

# Rodar aplicação em modo debug
python manage.py runserver

# Ver status de middlewares
python manage.py shell
>>> from tickets.middleware.config import MiddlewareConfig
>>> MiddlewareConfig.log_config()

# Limpar cache (útil para testar rate limiting)
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Verificar logs em tempo real
tail -f logs/middleware.log
tail -f logs/activity.log
tail -f logs/security.log

# Analisar performance
grep "SLOW REQUEST" logs/performance.log | head -20

# Encontrar erros
grep "ERROR\|CRITICAL" logs/errors.log

# Limpar arquivos de log antigos
find logs/ -name "*.log.*" -mtime +30 -delete

# Comprimir logs antigos
gzip logs/middleware.log.*

# Buscar atividades de usuário específico
grep "username=admin" logs/activity.log
"""


# ============================================================================
# DOCUMENTAÇÃO REFERÊNCIA
# ============================================================================

"""
Para mais detalhes, consulte:

1. README.md
   - Visão geral completa
   - Configuração de cada middleware
   - Guia de boas práticas

2. ARCHITECTURE.md
   - Fluxo de requisição/resposta
   - Diagramas de segurança
   - Ordem de execução

3. examples.py
   - Exemplos de código
   - Padrões de uso
   - Integração com views

4. tests.py
   - Testes unitários
   - Testes de integração
   - Testes de performance
"""
