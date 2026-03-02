# Middleware Layer Documentation

## Overview

A camada de middleware completa para a aplicação Django Helpdesk fornece:

- ✅ Autenticação e Autorização
- ✅ Logging e Monitoramento
- ✅ Segurança (Rate Limiting, CORS, Validação)
- ✅ Tratamento de Erros
- ✅ Processamento de Respostas (Compressão, Cache)

## Estrutura de Middlewares

### 1. Authentication Middleware (`authentication.py`)

#### `AuthenticationMiddleware`
Verifica autenticação de usuário em cada requisição.

**Funcionalidades:**
- Valida sessões de usuário
- Redireciona usuários não autenticados
- Rastreia IP e User-Agent
- Log de tentativas não autorizadas

**Configuração:**
```python
PUBLIC_URLS = [
    '/admin/login/',
    '/login/',
    '/register/',
    '/password-reset/',
    '/static/',
]
```

#### `PermissionMiddleware`
Implementa controle de acesso baseado em papéis (RBAC).

**Papéis Suportados:**
- `admin`: Acesso completo
- `gestor`: Gerenciamento de tickets
- `colaborador`: Criar tickets

#### `SessionSecurityMiddleware`
Enforce políticas de segurança de sessão.

**Configurações:**
- `SESSION_TIMEOUT`: 3600s (1 hora)
- `INACTIVITY_TIMEOUT`: 1800s (30 minutos)

---

### 2. Logging Middleware (`logging.py`)

#### `RequestLoggingMiddleware`
Registra todos os requisições com detalhes.

**Features:**
- Log automático de POST/PUT/DELETE/PATCH
- Mascara dados sensíveis (senha, token, etc)
- Extrai IP do cliente
- Rastreia User-Agent

**Sensible Fields Mascaradas:**
```python
['password', 'token', 'secret', 'api_key', 'credit_card']
```

#### `UserActivityMiddleware`
Rastreia atividades de usuário para auditoria.

**Campos Rastreados:**
- User ID e Username
- Método HTTP
- Caminho da requisição
- IP Address
- User-Agent
- Timestamp

#### `PerformanceMonitoringMiddleware`
Monitora métricas de performance.

**Métricas:**
- Tempo de resposta
- Contagem de queries do banco
- Detecção de requisições lentas (> 1s)
- Logging detalhado de performance

---

### 3. Security Middleware (`security.py`)

#### `RateLimitingMiddleware`
Protege contra abuso com rate limiting.

**Limites por Minuto:**
- Usuários anônimos: 30 requisições
- Usuários autenticados: 100 requisições
- Administradores: 500 requisições

**Features:**
- Blacklist automática após violações repetidas
- Cache-based implementation
- Duration de blacklist: 1 hora

#### `SecurityHeadersMiddleware`
Adiciona headers de segurança a todas as respostas.

**Headers Adicionados:**
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: [restrictive policy]
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: [restricted permissions]
Strict-Transport-Security: max-age=31536000 (production)
```

#### `RequestValidationMiddleware`
Valida requisições para segurança básica.

**Validações:**
- Tamanho máximo do corpo: 10 MB
- Detecta padrões suspeitos (SQL injection, XSS)
- Previne requisições malformadas

#### `CORSMiddleware`
Gerencia requisições Cross-Origin.

**Origens Permitidas:**
```python
[
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
]
```

---

### 4. Error Handling Middleware (`error_handling.py`)

#### `ErrorHandlingMiddleware`
Captura e registra exceções gracefully.

**Features:**
- Registra stack trace completo
- Log de tipo de erro e mensagem
- Response genérica em produção
- Detalhes em modo debug

#### `Http404Middleware`
Registra erros 404 com contexto.

**Informações Registradas:**
- Usuário responsável
- IP do cliente
- Caminho solicitado
- Referrer

#### `Http500Middleware`
Registra erros críticos 500.

#### `ValidationErrorMiddleware`
Rastreia erros de validação (400, 403).

---

### 5. Response Processing Middleware (`response_processing.py`)

#### `ResponseFormattingMiddleware`
Formata respostas consistentemente.

**Features:**
- Adiciona Content-Length se necessário
- Adiciona headers de segurança
- Formata respostas JSON

#### `CompressionMiddleware`
Comprime respostas com GZIP.

**Configuração:**
- Tamanho mínimo: 512 bytes
- Tipos compressíveis: HTML, CSS, JS, JSON, XML, SVG
- Nível de compressão: 6

#### `CacheControlMiddleware`
Define headers de cache apropriados.

**Períodos de Cache:**
- Arquivos estáticos: 1 ano
- HTML: 1 hora
- JSON: 5 minutos
- Padrão: No cache

#### `ContentLengthMiddleware`
Garante header Content-Length em todas as respostas.

---

## Configuração

### Habilitar/Desabilitar Middlewares

Edite `tickets/middleware/config.py`:

```python
ENABLED_MIDDLEWARE = {
    'authentication': True,
    'permission': True,
    'session_security': True,
    'request_logging': True,
    'rate_limiting': True,
    # ... etc
}
```

### Personalizar Limites de Rate Limiting

Em `tickets/middleware/config.py`:

```python
SECURITY_CONFIG = {
    'rate_limit_anonymous': 30,
    'rate_limit_authenticated': 100,
    'rate_limit_admin': 500,
    'blacklist_duration': 3600,
    'session_timeout': 3600,
    'inactivity_timeout': 1800,
}
```

### Adicionar URLs Públicas

Em `tickets/middleware/config.py`:

```python
PUBLIC_URLS = [
    '/admin/login/',
    '/login/',
    '/register/',
    # Adicione suas URLs públicas aqui
]
```

---

## Logging

### Estrutura de Logs

```
logs/
├── middleware.log          # Operações gerais de middleware
├── activity.log            # Auditoria de atividades de usuário
├── security.log            # Eventos de segurança
├── errors.log              # Erros da aplicação
└── performance.log         # Métricas de performance
```

### Configuração de Logging

A configuração automática em `tickets/middleware/logging_config.py`:

- **Tamanho máximo**: 10 MB por arquivo
- **Backup**: 5 arquivos anteriores mantidos
- **Formato**: `[YYYY-MM-DD HH:MM:SS] LEVEL - Message`
- **Console output**: Ativado em modo DEBUG

### Exemplo de Logs

**Activity Log:**
```json
{"user_id": 1, "username": "admin", "method": "POST", "path": "/tickets/create/", "ip_address": "127.0.0.1", "timestamp": 1677000000}
```

**Security Log:**
```
[2024-01-15 10:30:45] WARNING - Rate limit exceeded for user_1 (100/100 requests)
[2024-01-15 10:31:20] ERROR - IP blacklisted due to repeated violations: ip_192.168.1.100
```

**Performance Log:**
```
[2024-01-15 10:30:45] WARNING - SLOW REQUEST | {"method": "GET", "path": "/tickets/list/", "status": 200, "response_time_ms": 1250.34, "database_queries": 15}
```

---

## Ordem de Execução (Importante!)

A ordem dos middlewares em `MIDDLEWARE` é crítica:

1. **Response Processing** (primeiro - early binding)
   - ResponseFormattingMiddleware
   - CompressionMiddleware

2. **Request Processing**
   - RequestLoggingMiddleware
   - RequestValidationMiddleware
   - CORSMiddleware

3. **Authentication/Authorization**
   - AuthenticationMiddleware
   - PermissionMiddleware
   - SessionSecurityMiddleware

4. **Security**
   - RateLimitingMiddleware
   - SecurityHeadersMiddleware

5. **Monitoring**
   - UserActivityMiddleware
   - PerformanceMonitoringMiddleware

6. **Error Handling** (último - late binding)
   - ErrorHandlingMiddleware

---

## Casos de Uso

### Auditoria Completa
Rastreie todas as ações de usuário verificando:
- `logs/activity.log` - Registro detalhado
- `logs/security.log` - Eventos de segurança
- Database audit trail (se configurado)

### Detecção de Ataques
Monitore:
- `logs/security.log` para tentativas de rate limiting
- `logs/errors.log` para padrões suspeitos
- IPs blacklisteados após violações repetidas

### Performance Tuning
Analise:
- `logs/performance.log` para requisições lentas
- Database query counts
- Response times por endpoint

### Debug de Problemas
Use:
- `logs/middleware.log` para contexto geral
- `logs/errors.log` para stack traces
- `logs/activity.log` para reproduzir sequência de eventos

---

## Boas Práticas

### 1. Segurança
```python
# ✅ Sempre mascare dados sensíveis
SENSITIVE_FIELDS = ['password', 'token', 'secret', 'api_key']

# ✅ Configure rate limiting apropriado
rate_limit_anonymous = 30  # Mais restritivo

# ✅ Use HTTPS em produção
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
```

### 2. Performance
```python
# ✅ Comprima respostas grandes
CompressionMiddleware.MIN_SIZE = 512

# ✅ Configure cache apropriadamente
CACHE_CONFIG = {
    'static_cache_age': 31536000,  # 1 ano para static
    'json_cache_age': 300,  # 5 minutos para API
}

# ✅ Monitore requisições lentas
PERFORMANCE_CONFIG['slow_request_threshold'] = 1.0
```

### 3. Logging
```python
# ✅ Use níveis apropriados
logging.DEBUG  # Desenvolvimento
logging.INFO   # Produção

# ✅ Mantenha log rotation
maxBytes=10 * 1024 * 1024  # 10 MB
backupCount=5  # Manter 5 anteriores

# ✅ Exclua logs de versionamento
echo "logs/" >> .gitignore
```

### 4. Debugging
```python
# ✅ Use request/response logging
logger.debug(f"Request: {method} {path}")

# ✅ Rastreie atividades de usuário
activity_logger.info(json.dumps(activity_data))

# ✅ Monitore performance
logger.warning(f"SLOW REQUEST | {elapsed_time:.2f}s")
```

---

## Troubleshooting

### Rate Limiting Muito Restritivo
```python
# Aumentar limites em config.py
SECURITY_CONFIG['rate_limit_authenticated'] = 200
```

### Middleware Causando Lentidão
```python
# Desabilitar em config.py
ENABLED_MIDDLEWARE['compression'] = False
ENABLED_MIDDLEWARE['performance_monitoring'] = False
```

### Logs Não Aparecem
```python
# Verificar permissões de arquivo
chmod 755 logs/

# Verificar nível de logging
logger.setLevel(logging.DEBUG)  # Em settings.py
```

### CORS Erro
```python
# Adicionar origem em SecurityMiddleware
ALLOWED_ORIGINS = [
    'http://seu-frontend.com',
    'http://localhost:3000',
]
```

---

## Exemplo de Integração Completa

```python
# settings.py
from tickets.middleware.logging_config import configure_middleware_logging

# Configurar logging
configure_middleware_logging()

# Adicionar middlewares (já feito em settings.py)
MIDDLEWARE = [
    # ... middlewares ...
]

# Usar logging em views
import logging
logger = logging.getLogger('helpdesk.middleware')

def my_view(request):
    logger.info(f"User {request.user.username} accessing resource")
    # ... view logic ...
```

---

## Próximos Passos

1. ✅ Implementar autenticação OAuth/JWT
2. ✅ Adicionar honeypot fields para CSRF
3. ✅ Integrar com serviço de alertas (email, Slack)
4. ✅ Adicionar métricas Prometheus para monitoring
5. ✅ Implementar WAF (Web Application Firewall) rules

---

**Documentação Criada:** Janeiro 2026  
**Django Version:** 6.0.1  
**Python Version:** 3.9+
