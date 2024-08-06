import logging
import logging.handlers
from constant.databaseconstant import log_file

def setup_logging(log_file):
    """
    Set up logging configuration to save exceptions and events to log files.

    Parameters:
        log_file (str): The base filename for the log files.

    Returns:
        None
    """
    # Set up the logger
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.DEBUG)

    # Set up the log rotation handler (10MB per file, max 3 files)
    file_handler = logging.handlers.RotatingFileHandler(filename=log_file, maxBytes=10*1024*1024, backupCount=3)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))

    # Add the handler to the logger
    logger.addHandler(file_handler)

    # Set up console logging for debugging (optional)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
    logger.addHandler(console_handler)

def log_exception(exception):
    """
    Log an exception with traceback.

    Parameters:
        exception (Exception): The exception to log.

    Returns:
        None
    """
    logger = logging.getLogger("my_logger")
    logger.exception(exception)

def log_debug(message):
    """
    Log a debug message.

    Parameters:
        message (str): The debug message to log.

    Returns:
        None
    """
    logger = logging.getLogger("my_logger")
    logger.debug(message)

def log_event(message):
    """
    Log an event to the log file.

    Parameters:
        message (str): The message to log.

    Returns:
        None
    """
    logger = logging.getLogger("my_logger")
    logger.info(message)

# # Usage example
try:
    
    setup_logging(log_file)
except Exception as e:

    print(f"Erro as{e}")
    
#     try:
#         # Code that may raise exceptions goes here
#         raise ValueError("Example exception")
#     except Exception as e:
#         log_exception(e)

#     log_event("Event {}: Something happened.".format())
#     log_event("Event 2: Another event occurred.")
