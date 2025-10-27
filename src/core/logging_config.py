import sys
import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    """
    Intercepts standard logging messages and redirects them to Loguru.
    """
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging():
    """
    Configures the Loguru logger for the application.
    Removes default handlers and adds a new one with a custom format.
    """
    logger.remove() # Remove default handler to avoid duplicates.

    # General purpose logger for INFO level, excluding user-related logs to avoid duplication.
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{line}</cyan> - <level>{message}</level>",
        colorize=True,
        filter=lambda record: record["level"].name == "INFO" and "user" not in record["name"]
    )

    # Logger for WARNING and ERROR levels to make them stand out.
    logger.add(
        sys.stderr,
        level="WARNING",
        format="<yellow>{time:HH:mm:ss}</yellow> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # Specific logger for all modules containing 'user' in their name.
    logger.add(
        sys.stderr,
        level="INFO",
        format="<blue>👤 {time:HH:mm:ss}</blue> | <level>{level: <8}</level> | <cyan>{name}:{line}</cyan> - <level>{message}</level>",
        colorize=True,
        filter=lambda record: "user" in record["name"]
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)