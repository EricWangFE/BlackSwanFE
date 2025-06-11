"""Structured logging configuration"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
import structlog
from structlog.processors import JSONRenderer, TimeStamper, add_log_level


def setup_logger(service_name: str = "blackswan") -> structlog.BoundLogger:
    """Configure structured logging"""
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            add_metadata_processor,
            JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logger = structlog.get_logger(service_name)
    return logger


def add_metadata_processor(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add custom metadata to all log entries"""
    event_dict["service"] = "blackswan"
    event_dict["environment"] = "production"
    
    # Add trace ID if available
    if hasattr(logger, "_context") and "trace_id" in logger._context:
        event_dict["trace_id"] = logger._context["trace_id"]
    
    return event_dict


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a configured logger instance"""
    if not name:
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get("__name__", "blackswan")
        else:
            name = "blackswan"
    
    return structlog.get_logger(name)