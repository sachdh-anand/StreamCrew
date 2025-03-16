import sys
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
sys.path.append(str(src_dir.parent))

from src.utils.logger import get_logger

# Get a test logger
logger = get_logger("test_logger")

# Test logging with different levels
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")

print("Logger test completed. Check the logs directory for the log file.") 