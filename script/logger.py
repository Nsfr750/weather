"""
Logging configuration for the Weather Application.

This module sets up logging with both file and console handlers,
and provides a function to get a logger instance.
"""
import os
import logging
from pathlib import Path
from datetime import datetime

# Import language manager
from lang.language_manager import LanguageManager

def _close_handlers(logger):
    """Close and remove all handlers from the logger."""
    for handler in logger.handlers[:]:
        try:
            if hasattr(handler, 'close'):
                handler.close()
            logger.removeHandler(handler)
        except Exception as e:
            print(f"Error closing handler: {e}")

def setup_logging():
    """
    Set up logging configuration for the application.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create a logger with the module's name
    logger = logging.getLogger('script.logger')
    
    # Close and clear any existing handlers to avoid duplicate logs and file locks
    _close_handlers(logger)
    
    # Set the default level to DEBUG to capture all levels of logs
    logger.setLevel(logging.DEBUG)
    
    # Ensure logs directory exists
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Create log file with date only (one file per day)
    log_date = datetime.now().strftime('%Y%m%d')
    log_file = log_dir / f'weather_{log_date}.log'
    
    try:
        # Create formatter
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s')
        
        # Create file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Prevent the logger from propagating to the root logger
        logger.propagate = False
        
        logger.debug('Logger initialized')
        return logger
    except Exception as e:
        # If there's an error setting up logging, clean up and re-raise
        _close_handlers(logger)
        raise

# Create a module-level logger instance
logger = setup_logging()
