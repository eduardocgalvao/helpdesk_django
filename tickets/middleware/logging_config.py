"""
Logging configuration for middleware.

Sets up loggers for:
- General middleware operations
- User activities and audit trail
- Security events
- Error logging
- Performance monitoring
"""

import logging
import logging.handlers
from pathlib import Path
from django.conf import settings

# Create logs directory if it doesn't exist
LOGS_DIR = Path(settings.BASE_DIR) / 'logs'
LOGS_DIR.mkdir(exist_ok=True)


def configure_middleware_logging():
    """
    Configure all middleware loggers.
    """
    
    # Main middleware logger
    configure_logger(
        'helpdesk.middleware',
        LOGS_DIR / 'middleware.log',
        'General middleware operations'
    )
    
    # Activity/Audit logger
    configure_logger(
        'helpdesk.activity',
        LOGS_DIR / 'activity.log',
        'User activities and audit trail'
    )
    
    # Security logger
    configure_logger(
        'helpdesk.security',
        LOGS_DIR / 'security.log',
        'Security events and warnings'
    )
    
    # Error logger
    configure_logger(
        'helpdesk.errors',
        LOGS_DIR / 'errors.log',
        'Application errors and exceptions'
    )
    
    # Performance logger
    configure_logger(
        'helpdesk.performance',
        LOGS_DIR / 'performance.log',
        'Performance metrics and monitoring'
    )


def configure_logger(logger_name, log_file, description):
    """
    Configure an individual logger.
    """
    logger = logging.getLogger(logger_name)
    
    # Skip if already configured
    if logger.handlers:
        return logger
    
    # Set logger level
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Create formatters
    if settings.DEBUG:
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # File handler (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (for development)
    if settings.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    logger.info(f"Logger configured: {description} (Level: {'DEBUG' if settings.DEBUG else 'INFO'})")
    
    return logger


# Initialize logging on import
if not getattr(configure_middleware_logging, '_initialized', False):
    try:
        configure_middleware_logging()
        configure_middleware_logging._initialized = True
    except Exception as e:
        print(f"Error configuring middleware logging: {str(e)}")
