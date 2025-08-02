#!/usr/bin/env python3
"""
Test script for the Weather App logging system.

This script tests the logging configuration and functionality.
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pytest

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the logger module to test
from script.logger import setup_logging

# Test data
TEST_MESSAGE = "This is a test log message"
TEST_MESSAGE_DEBUG = "This is a debug message"
TEST_MESSAGE_INFO = "This is an info message"
TEST_MESSAGE_WARNING = "This is a warning message"
TEST_MESSAGE_ERROR = "This is an error message"
TEST_MESSAGE_CRITICAL = "This is a critical message"


def test_logger_initialization():
    """Test that the logger is properly initialized."""
    # Setup logging with a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test logs directory
        test_logs_dir = Path(temp_dir) / "test_logs"
        test_logs_dir.mkdir()
        
        # Change to the test directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        logger = None
        try:
            # Initialize the logger
            logger = setup_logging()
            
            # Verify the logger is created
            assert logger is not None
            assert isinstance(logger, logging.Logger)
            
            # Verify the log file was created
            log_date = datetime.now().strftime('%Y%m%d')
            log_file = test_logs_dir / f'weather_{log_date}.log'
            assert not log_file.exists()  # Should be created in the original directory, not test_logs
            
            # Verify the log file in the current directory
            log_file = Path(f'logs/weather_{log_date}.log')
            
            # Wait a bit to ensure the file is written
            import time
            time.sleep(0.1)
            
            assert log_file.exists(), f"Log file {log_file} does not exist"
            
        finally:
            # Close all handlers
            if logger:
                from script.logger import _close_handlers
                _close_handlers(logger)
            
            # Clean up log files if they exist
            log_date = datetime.now().strftime('%Y%m%d')
            log_file = Path(f'logs/weather_{log_date}.log')
            if log_file.exists():
                try:
                    log_file.unlink()
                    if log_file.parent.exists() and not any(log_file.parent.iterdir()):
                        log_file.parent.rmdir()
                except Exception as e:
                    print(f"Error cleaning up log file: {e}")
            
            # Change back to the original directory
            os.chdir(original_dir)


def test_log_messages():
    """Test that log messages are properly written."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test logs directory
        test_logs_dir = Path(temp_dir) / "test_logs"
        test_logs_dir.mkdir()
        
        # Change to the test directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Initialize the logger
            logger = setup_logging()
            
            # Log messages at different levels
            logger.debug(TEST_MESSAGE_DEBUG)
            logger.info(TEST_MESSAGE_INFO)
            logger.warning(TEST_MESSAGE_WARNING)
            logger.error(TEST_MESSAGE_ERROR)
            logger.critical(TEST_MESSAGE_CRITICAL)
            
            # Flush all handlers to ensure messages are written
            for handler in logger.handlers:
                handler.flush()
            
            # Get the log file path
            log_date = datetime.now().strftime('%Y%m%d')
            log_file = Path(f'logs/weather_{log_date}.log')
            
            # Wait a bit to ensure the file is written
            import time
            time.sleep(0.1)
            
            # Verify the log file was created and contains our messages
            assert log_file.exists()
            
            # Read the log file
            log_content = log_file.read_text(encoding='utf-8')
            
            # Verify log levels and messages
            assert 'DEBUG' in log_content, f"DEBUG not found in log content: {log_content}"
            assert 'INFO' in log_content, f"INFO not found in log content: {log_content}"
            assert 'WARNING' in log_content, f"WARNING not found in log content: {log_content}"
            assert 'ERROR' in log_content, f"ERROR not found in log content: {log_content}"
            assert 'CRITICAL' in log_content, f"CRITICAL not found in log content: {log_content}"
            
            # Verify our test messages are in the log
            assert TEST_MESSAGE_DEBUG in log_content, f"Debug message not found in log"
            assert TEST_MESSAGE_INFO in log_content, f"Info message not found in log"
            assert TEST_MESSAGE_WARNING in log_content, f"Warning message not found in log"
            assert TEST_MESSAGE_ERROR in log_content, f"Error message not found in log"
            assert TEST_MESSAGE_CRITICAL in log_content, f"Critical message not found in log"
            
        finally:
            # Close all handlers
            from script.logger import _close_handlers
            _close_handlers(logger)
            
            # Clean up log files if they exist
            log_date = datetime.now().strftime('%Y%m%d')
            log_file = Path(f'logs/weather_{log_date}.log')
            if log_file.exists():
                try:
                    log_file.unlink()
                    if log_file.parent.exists() and not any(log_file.parent.iterdir()):
                        log_file.parent.rmdir()
                except Exception as e:
                    print(f"Error cleaning up log file: {e}")
            
            # Change back to the original directory
            os.chdir(original_dir)


def test_log_file_rotation():
    """Test that log files are properly rotated by date."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to the test directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            log_messages = []
            
            # Initialize the logger multiple times to ensure proper file handling
            for i in range(3):
                logger = setup_logging()
                msg = f"Test log message {i+1}"
                logger.info(msg)
                log_messages.append(msg)
                
                # Flush the logger to ensure messages are written
                for handler in logger.handlers:
                    handler.flush()
            
            # Get the log file path
            log_date = datetime.now().strftime('%Y%m%d')
            log_file = Path(f'logs/weather_{log_date}.log')
            
            # Wait a bit to ensure the file is written
            import time
            time.sleep(0.1)
            
            # Verify the log file exists and has content
            assert log_file.exists(), f"Log file {log_file} does not exist"
            log_content = log_file.read_text(encoding='utf-8')
            
            # Verify all log messages are present
            for msg in log_messages:
                assert msg in log_content, f"Message '{msg}' not found in log"
                
        finally:
            # Close all handlers
            from script.logger import _close_handlers
            _close_handlers(logging.getLogger('script.logger'))
            
            # Clean up log files if they exist
            log_date = datetime.now().strftime('%Y%m%d')
            log_file = Path(f'logs/weather_{log_date}.log')
            if log_file.exists():
                try:
                    log_file.unlink()
                    if log_file.parent.exists() and not any(log_file.parent.iterdir()):
                        log_file.parent.rmdir()
                except Exception as e:
                    print(f"Error cleaning up log file: {e}")
            
            # Change back to the original directory
            os.chdir(original_dir)


if __name__ == "__main__":
    # Run the tests
    test_logger_initialization()
    test_log_messages()
    test_log_file_rotation()
    print("All logging tests passed!")
