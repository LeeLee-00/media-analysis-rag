import logging
import sys
from pathlib import Path
from app.core.config import LOG_PATH

LOG_LEVEL = logging.DEBUG  # Can switch to INFO or WARNING in prod
LOG_FILE = Path(LOG_PATH)

# Ensure logs directory exists
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(formatter)

# File Handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(formatter)

# Root logger config
def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.propagate = False

    return logger

