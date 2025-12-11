
import os
import logging
from loguru import logger
from django.utils.log import DEFAULT_LOGGING

# Configure log file path
log_path = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_path, exist_ok=True)

# Add log handlers
logger.remove()  # Remove default handler
logger.add(
    os.path.join(log_path, "app.log"),
    rotation="10 MB",  # Rotate log after 10 MB
    retention="7 days",  # Keep logs for 7 days
    compression="zip",  # Compress rotated logs
    level="DEBUG",  # Logging level
    format="{time} - {level} - {message}",
)
logger.add(logging.StreamHandler(),level="DEBUG",  # Logging level
    format="{time} - {level} - {message}")

# Replace Django's default logging with Loguru
class InterceptHandler:
    """
    A handler to bridge standard logging with Loguru.
    """
    def __init__(self, level):
        self.level = level

    def emit(self, record):
        loguru_level = logger.level(record.levelname).name
        logger.log(loguru_level, record.getMessage())

for level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
    logging.getLogger(level).addHandler(InterceptHandler(level))



# import logging.handlers
# import os
# import logging
# from loguru import logger

# # Configure log file path
# log_path = os.path.join(os.path.dirname(__file__), 'logs')
# os.makedirs(log_path, exist_ok=True)

# # Add log handlers
# logger.remove()  # Remove the default handler
# logger.add(
#     os.path.join(log_path, "app.log"),
#     rotation="10 MB",  # Rotate log after 10 MB
#     retention="7 days",  # Keep logs for 7 days
#     compression="zip",  # Compress rotated logs
#     level="DEBUG",  # Logging level
#     format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}",
# )


# class InterceptHandler(logging.Handler):
#     """
#     A handler to bridge standard logging with Loguru.
#     """
#     def emit(self, record):
#         # Get the corresponding Loguru level
#         loguru_level = getattr(logger, record.levelname.lower(), "info")
#         # Log with Loguru, including exception information if present
#         logger.opt(exception=record.exc_info).log(loguru_level, record.getMessage())

# console_handler = logging.StreamHandler()

# # Remove all existing handlers from Django's default logging configuration
# for handler in logging.root.handlers[:]:
#     logging.root.removeHandler(handler)

# # Intercept standard logging to use Loguru
# logging.basicConfig(handlers=[InterceptHandler(), console_handler], level=logging.DEBUG)


# # # Set up Django logging to use Loguru instead
# # logging.root.addHandler(InterceptHandler())
