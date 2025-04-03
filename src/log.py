import sys

from loguru import logger

from src.config import LOGGING_FORMAT, ROOT_DIR

logger.remove()
logger.add(
    ROOT_DIR / "logs" / "log_{time:YYYY-MM-DD}.log",
    format=LOGGING_FORMAT,
    level="DEBUG",
    mode="a",
    retention="5 days",
)
logger.add(sys.stdout, format=LOGGING_FORMAT)
