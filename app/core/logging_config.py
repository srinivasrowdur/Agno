import logging
import logging.config
import os
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import LOG_LEVEL, ENVIRONMENT

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['app'] = 'agno-api'
        log_record['environment'] = ENVIRONMENT
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

def setup_logging():
    """Configure logging based on environment."""
    
    log_level = getattr(logging, LOG_LEVEL)
    
    if ENVIRONMENT == "production":
        # JSON logging for production
        log_handler = logging.StreamHandler(sys.stdout)
        formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
        log_handler.setFormatter(formatter)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            handlers=[log_handler]
        )
    else:
        # Human-readable logging for development
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
    
    # Reduce noise from third-party libraries
    for logger_name in ['uvicorn.access', 'urllib3.connectionpool']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging configured with level: {LOG_LEVEL}")
    
    return logger 