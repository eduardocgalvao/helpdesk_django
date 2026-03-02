# Middleware Layer Architecture

## 📁 Estrutura de Diretórios

```
tickets/middleware/
├── __init__.py                      # Package initialization
├── authentication.py                # Authentication & Authorization
│   ├── AuthenticationMiddleware
│   ├── PermissionMiddleware
│   └── SessionSecurityMiddleware
├── logging.py                       # Logging & Activity Tracking
│   ├── RequestLoggingMiddleware
│   ├── UserActivityMiddleware
│   └── PerformanceMonitoringMiddleware
├── security.py                      # Security & Protection
│   ├── RateLimitingMiddleware
│   ├── SecurityHeadersMiddleware
│   ├── RequestValidationMiddleware
│   └── CORSMiddleware
├── error_handling.py                # Error & Exception Handling
│   ├── ErrorHandlingMiddleware
│   ├── Http404Middleware
│   ├── Http500Middleware
│   └── ValidationErrorMiddleware
├── response_processing.py           # Response Optimization
│   ├── ResponseFormattingMiddleware
│   ├── CompressionMiddleware
│   ├── CacheControlMiddleware
│   ├── XContentTypeOptionsMiddleware
│   └── ContentLengthMiddleware
├── config.py                        # Configuration & Utils
│   ├── MiddlewareConfig
│   └── MiddlewareUtils
├── logging_config.py                # Logger Configuration
├── tests.py                         # Unit & Integration Tests
├── examples.py                      # Usage Examples
└── README.md                        # Documentation
```

## 🔄 Request/Response Flow

```
REQUEST
  ↓
[1] ResponseFormattingMiddleware ──────────────┐
    (early binding)                             │
  ↓                                             │
[2] CompressionMiddleware                       │
  ↓                                             │
[3] RequestLoggingMiddleware                    │
  ↓                                             │
[4] RequestValidationMiddleware                 │
  ↓                                             │
[5] CORSMiddleware                              │
  ↓                                             │
[6] AuthenticationMiddleware                    │
  ↓                                             │
[7] PermissionMiddleware                        │
  ↓                                             │
[8] SessionSecurityMiddleware                   │
  ↓                                             │
[9] RateLimitingMiddleware                      │
  ↓                                             │
[10] SecurityHeadersMiddleware                  │
  ↓                                             │
[11] UserActivityMiddleware                     │
  ↓                                             │
[12] PerformanceMonitoringMiddleware            │
  ↓                                             │
[13] ErrorHandlingMiddleware ←──────────────────┤
     (late binding)                             │
  ↓                                             │
[14] VIEW PROCESSING                            │
  ↓                                             ↓
RESPONSE                           [CacheControlMiddleware]
  ↓                                [ContentLengthMiddleware]
  ↓                                [XContentTypeOptionsMiddleware]
[RESPONSE HANDLERS]
```

## 🛡️ Security Layers

```
┌─────────────────────────────────────────────────────┐
│                  SECURITY LAYERS                     │
├─────────────────────────────────────────────────────┤
│ [L1] Input Validation                               │
│      ├─ Request body size validation                │
│      ├─ Suspicious content detection                │
│      └─ CORS origin verification                    │
├─────────────────────────────────────────────────────┤
│ [L2] Authentication                                  │
│      ├─ User session verification                   │
│      ├─ Login redirect for anonymous users          │
│      └─ Session timeout handling                    │
├─────────────────────────────────────────────────────┤
│ [L3] Authorization                                   │
│      ├─ Role-based access control (RBAC)           │
│      ├─ Permission verification                     │
│      └─ Group-based permissions                     │
├─────────────────────────────────────────────────────┤
│ [L4] Rate Limiting & Throttling                      │
│      ├─ Per-user rate limits                        │
│      ├─ IP-based rate limits                        │
│      ├─ Automatic blacklisting                      │
│      └─ Cache-based implementation                  │
├─────────────────────────────────────────────────────┤
│ [L5] Security Headers                                │
│      ├─ X-Frame-Options (Clickjacking)              │
│      ├─ X-Content-Type-Options (MIME sniffing)      │
│      ├─ X-XSS-Protection                            │
│      ├─ Content-Security-Policy                     │
│      ├─ HSTS (in production)                        │
│      └─ Referrer-Policy                             │
├─────────────────────────────────────────────────────┤
│ [L6] Output Encoding & Validation                    │
│      ├─ Response type validation                    │
│      ├─ GZIP compression                            │
│      └─ Cache control headers                       │
└─────────────────────────────────────────────────────┘
```

## 📊 Logging Architecture

```
┌──────────────────────────────────────┐
│         LOG COLLECTION               │
├──────────────────────────────────────┤
│                                      │
│  RequestLoggingMiddleware            │
│  ├─ GET requests (debug)             │
│  └─ POST/PUT/DELETE (info)           │
│                                      │
│  UserActivityMiddleware              │
│  ├─ User actions                     │
│  └─ Audit trail                      │
│                                      │
│  PerformanceMonitoringMiddleware     │
│  ├─ Response times                   │
│  ├─ DB queries                       │
│  └─ Slow requests (>1s)              │
│                                      │
│  ErrorHandlingMiddleware             │
│  ├─ Exceptions                       │
│  └─ Stack traces                     │
│                                      │
└──────────────────────────────────────┘
           ↓↓↓ (structured logging) ↓↓↓
┌──────────────────────────────────────┐
│      LOG AGGREGATION                 │
├──────────────────────────────────────┤
│                                      │
│  logs/middleware.log                 │
│  ├─ General operations               │
│  ├─ 10 MB rotation                   │
│  └─ 5 backups kept                   │
│                                      │
│  logs/activity.log                   │
│  ├─ User activities                  │
│  ├─ Audit trail (JSON)               │
│  └─ Compliance tracking              │
│                                      │
│  logs/security.log                   │
│  ├─ Rate limiting events             │
│  ├─ Suspicious activities            │
│  └─ Security warnings                │
│                                      │
│  logs/errors.log                     │
│  ├─ Exception stack traces           │
│  ├─ 500 errors                       │
│  └─ Error details                    │
│                                      │
│  logs/performance.log                │
│  ├─ Slow requests                    │
│  ├─ Response times                   │
│  └─ DB query counts                  │
│                                      │
└──────────────────────────────────────┘
```

## 🔐 Authentication Flow

```
USER REQUEST
    ↓
╔═══════════════════════════════════╗
║ Is URL in PUBLIC_URLS?            ║
╚═══════════════════════════════════╝
    ↙                         ↘
   YES                         NO
    ↓                          ↓
Allow                ╔═══════════════════════════╗
                    ║ Is User Authenticated?    ║
                    ╚═══════════════════════════╝
                        ↙              ↘
                       YES              NO
                        ↓               ↓
                  Continue          Redirect
                              to /login/
                        ↓
            ╔═══════════════════════════════╗
            ║ Check User Role               ║
            ║ - Admin                       ║
            ║ - Gestor                      ║
            ║ - Colaborador                 ║
            ╚═══════════════════════════════╝
                        ↓
            ╔═══════════════════════════════╗
            ║ Check Rate Limits             ║
            ║ based on role                 ║
            ╚═══════════════════════════════╝
                ↙              ↘
              OK          EXCEEDED
                ↓               ↓
           Allow         Blacklist &
                         Return 429
```

## 📈 Performance Impact

```
┌─────────────────────────────────────────────────────┐
│           MIDDLEWARE OVERHEAD                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  RequestLoggingMiddleware          ~1-2ms            │
│  ├─ Log request data                                │
│  └─ Mask sensitive info                             │
│                                                      │
│  AuthenticationMiddleware          ~0.5-1ms         │
│  ├─ Session lookup                                  │
│  └─ URL check                                       │
│                                                      │
│  RateLimitingMiddleware            ~1-2ms           │
│  ├─ Cache lookup                                    │
│  └─ Rate limit calculation                          │
│                                                      │
│  PerformanceMonitoringMiddleware   ~0.5ms           │
│  ├─ Start timing                                    │
│  └─ Query counting                                  │
│                                                      │
│  SecurityHeadersMiddleware         ~0.1ms           │
│  ├─ Add response headers                            │
│  └─ Minimal processing                              │
│                                                      │
│  CompressionMiddleware             ~5-10ms          │
│  ├─ GZIP compression (depends on size)              │
│  └─ Large responses only                            │
│                                                      │
│  ────────────────────────────────────────────────   │
│  TOTAL OVERHEAD:                   ~8-16ms          │
│  (varies based on response size)                     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## 🎯 Middleware Responsibilities

```
┌──────────────────────┐
│  RequestValidation   │
├──────────────────────┤
│ - Size checking      │
│ - Content scanning   │
│ - Injection prevent  │
└──────────────────────┘
         ↓
┌──────────────────────┐
│  Authentication      │
├──────────────────────┤
│ - User verification  │
│ - Session check      │
│ - Login redirect     │
└──────────────────────┘
         ↓
┌──────────────────────┐
│  Authorization       │
├──────────────────────┤
│ - Role checking      │
│ - Permission verify  │
│ - RBAC enforce       │
└──────────────────────┘
         ↓
┌──────────────────────┐
│  RateLimiting        │
├──────────────────────┤
│ - Limit checking     │
│ - Blacklist manage   │
│ - Cache usage        │
└──────────────────────┘
         ↓
┌──────────────────────┐
│  Logging             │
├──────────────────────┤
│ - Request logging    │
│ - Activity tracking  │
│ - Performance mon.   │
└──────────────────────┘
         ↓
┌──────────────────────┐
│  View Execution      │
├──────────────────────┤
│ - Business logic     │
│ - Database access    │
│ - Response building  │
└──────────────────────┘
         ↓
┌──────────────────────┐
│  ResponseProcessing  │
├──────────────────────┤
│ - Formatting         │
│ - Compression        │
│ - Cache headers      │
│ - Security headers   │
└──────────────────────┘
         ↓
┌──────────────────────┐
│  ErrorHandling       │
├──────────────────────┤
│ - Exception catch    │
│ - Error logging      │
│ - Response format    │
└──────────────────────┘
         ↓
      CLIENT
```

## 📌 Configuration Summary

```
╔════════════════════════════════════════════════════╗
║         MIDDLEWARE CONFIGURATION                  ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  SECURITY SETTINGS:                               ║
║  ├─ Anonymous rate limit:     30 req/min          ║
║  ├─ Authenticated rate limit: 100 req/min         ║
║  ├─ Admin rate limit:         500 req/min         ║
║  ├─ Blacklist duration:       3600s (1h)          ║
║  ├─ Session timeout:          3600s (1h)          ║
║  ├─ Inactivity timeout:       1800s (30m)         ║
║  └─ Max request body:         10 MB               ║
║                                                    ║
║  PERFORMANCE SETTINGS:                            ║
║  ├─ Compression min size:     512 bytes           ║
║  ├─ Slow request threshold:   1.0 seconds         ║
║  ├─ Compression level:        6 (1-9)             ║
║  └─ Cache ages:               [See README]        ║
║                                                    ║
║  LOGGING SETTINGS:                                ║
║  ├─ Log rotation:             10 MB               ║
║  ├─ Backup count:             5 files             ║
║  ├─ Level (dev):              DEBUG               ║
║  ├─ Level (prod):             INFO                ║
║  └─ Log directory:            ./logs/             ║
║                                                    ║
╚════════════════════════════════════════════════════╝
```

## 🔗 Dependencies

```
Django 6.0+
├─ django.utils.deprecation (MiddlewareMixin)
├─ django.contrib.auth (Authentication)
├─ django.core.cache (Rate limiting)
├─ django.http (Response handling)
├─ django.shortcuts (Utilities)
└─ django.urls (URL reversal)

Python Standard Library
├─ logging (Logging)
├─ time (Performance tracking)
├─ json (Data serialization)
├─ gzip (Compression)
├─ io (Buffer handling)
└─ traceback (Error reporting)
```

## ✅ Checklist de Funcionalidades

- [x] Autenticação de usuário
- [x] Autorização baseada em papéis (RBAC)
- [x] Validação de sessão com timeout
- [x] Logging de requisições
- [x] Rastreamento de atividades (audit trail)
- [x] Monitoramento de performance
- [x] Rate limiting com blacklisting
- [x] Headers de segurança
- [x] Validação de requisições
- [x] CORS handling
- [x] Compressão de respostas
- [x] Cache control
- [x] Tratamento de erros
- [x] Logging estruturado
- [x] Utilitários de configuração

## 🚀 Next Steps

1. Configure logging em settings.py
2. Execute testes: `python manage.py test tickets.middleware`
3. Monitore logs durante desenvolvimento
4. Customize limites de rate limiting conforme necessário
5. Integre com ferramentas de monitoring (Sentry, ELK, etc.)

---

**Criado:** Janeiro 2026  
**Django Version:** 6.0.1  
**Python Version:** 3.9+
