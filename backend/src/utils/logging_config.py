"""
Logging configuration for FLB Nuclear Power Plant AI service.
Provides structured logging with request tracking and error handling.
"""

import logging
import logging.handlers
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class RequestFormatter(logging.Formatter):
    """
    Custom formatter that includes request context in log messages.
    """
    
    def format(self, record):
        """
        Format log record with additional context.
        
        Args:
            record: LogRecord instance
            
        Returns:
            str: Formatted log message
        """
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()
        
        # Add request ID if available
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'
        
        # Add model name if available
        if not hasattr(record, 'model_name'):
            record.model_name = 'N/A'
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True
) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        enable_console: Whether to enable console logging
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = RequestFormatter(
        fmt='%(timestamp)s - %(name)s - %(levelname)s - '
            'ReqID:%(request_id)s - Model:%(model_name)s - '
            '%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file or 'None'}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that automatically includes request context.
    """
    
    def __init__(self, logger: logging.Logger, extra: dict = None):
        """
        Initialize logger adapter.
        
        Args:
            logger: Base logger instance
            extra: Extra context to include in all log messages
        """
        super().__init__(logger, extra or {})
    
    def process(self, msg, kwargs):
        """
        Process log message and add extra context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
            
        Returns:
            tuple: Processed message and kwargs
        """
        # Add extra context to the log record
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        kwargs['extra'].update(self.extra)
        
        return msg, kwargs


def create_request_logger(
    base_logger: logging.Logger,
    request_id: str = None,
    model_name: str = None
) -> LoggerAdapter:
    """
    Create a logger adapter with request context.
    
    Args:
        base_logger: Base logger instance
        request_id: Request identifier
        model_name: Model name being used
        
    Returns:
        LoggerAdapter: Logger with request context
    """
    extra = {
        'request_id': request_id or 'N/A',
        'model_name': model_name or 'N/A'
    }
    
    return LoggerAdapter(base_logger, extra)


def log_request_start(
    logger: logging.Logger,
    endpoint: str,
    method: str,
    request_id: str = None,
    **kwargs
) -> None:
    """
    Log the start of a request.
    
    Args:
        logger: Logger instance
        endpoint: API endpoint
        method: HTTP method
        request_id: Request identifier
        **kwargs: Additional context
    """
    extra = {
        'request_id': request_id or 'N/A',
        'model_name': kwargs.get('model_name', 'N/A')
    }
    
    logger.info(
        f"Request started - {method} {endpoint}",
        extra=extra
    )


def log_request_end(
    logger: logging.Logger,
    endpoint: str,
    method: str,
    status_code: int,
    processing_time_ms: float,
    request_id: str = None,
    **kwargs
) -> None:
    """
    Log the end of a request.
    
    Args:
        logger: Logger instance
        endpoint: API endpoint
        method: HTTP method
        status_code: HTTP status code
        processing_time_ms: Processing time in milliseconds
        request_id: Request identifier
        **kwargs: Additional context
    """
    extra = {
        'request_id': request_id or 'N/A',
        'model_name': kwargs.get('model_name', 'N/A')
    }
    
    logger.info(
        f"Request completed - {method} {endpoint} - "
        f"Status: {status_code} - Time: {processing_time_ms:.2f}ms",
        extra=extra
    )


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: str = None,
    request_id: str = None,
    **kwargs
) -> None:
    """
    Log an error with context.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context about the error
        request_id: Request identifier
        **kwargs: Additional context
    """
    extra = {
        'request_id': request_id or 'N/A',
        'model_name': kwargs.get('model_name', 'N/A')
    }
    
    error_msg = f"Error: {type(error).__name__}: {str(error)}"
    if context:
        error_msg = f"{context} - {error_msg}"
    
    logger.error(error_msg, extra=extra, exc_info=True)


# Default logging configuration for development
def setup_development_logging():
    """Setup logging configuration optimized for development."""
    setup_logging(
        log_level="DEBUG",
        log_file=None,  # Console only for development
        enable_console=True
    )


# Default logging configuration for production
def setup_production_logging(log_dir: str = "logs"):
    """
    Setup logging configuration optimized for production.
    
    Args:
        log_dir: Directory to store log files
    """
    log_file = os.path.join(log_dir, "flb_nuclear_ai.log")
    
    setup_logging(
        log_level="INFO",
        log_file=log_file,
        max_file_size=50 * 1024 * 1024,  # 50MB
        backup_count=10,
        enable_console=False  # File only for production
    )