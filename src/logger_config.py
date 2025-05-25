"""
Logging configuration for the voice assistant.

This module sets up a global logger that can be imported and used
throughout the application.
"""

import logging
import sys

# Define the logging format
LOG_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
)
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Create a logger instance
logger = logging.getLogger('voice_assistant')
logger.setLevel(logging.DEBUG)  # Set the default level to DEBUG

# Create a handler for stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)  # Console output level
formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
stream_handler.setFormatter(formatter)

# Add the handler to the logger
if not logger.handlers:
    logger.addHandler(stream_handler)

# Example of how to add a file handler (optional)
# You might want to configure the file path and log level
# file_handler = logging.FileHandler("assistant.log")
# file_handler.setLevel(logging.DEBUG) # File logging level
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

# To use the logger in other modules:
# from .logger_config import logger  (if in the same directory)
# from ..core.logger_config import logger (if in a subdirectory like src/agents_def)
#
# logger.debug("This is a debug message.")
# logger.info("This is an info message.")
# logger.warning("This is a warning message.")
# logger.error("This is an error message.")
# logger.critical("This is a critical message.")
# try:
#     1 / 0
# except ZeroDivisionError:
#     logger.exception("Caught an exception:")
