from loguru import logger
import sys

# Configure Loguru
logger.remove()  # Remove default logger
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")  # Add console output
logger.add("logs/app.log", rotation="10 MB", retention="10 days", level="INFO")  # File output

def get_logger(name: str):
    return logger.bind(service=name)
