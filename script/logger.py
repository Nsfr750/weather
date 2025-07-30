"""
Logging configuration for the Weather Application.

This module sets up logging with both file and console handlers,
and provides a function to get a logger instance.
"""
import os
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """
    Set up logging configuration for the application.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Ensure logs directory exists
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Create log file with timestamp
    log_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'weather_app_{log_timestamp}.log'
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f'Logging to file: {log_file}')
    
    return logger

# Create a module-level logger instance
logger = setup_logging()
