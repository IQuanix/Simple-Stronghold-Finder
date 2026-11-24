# This logs into a file
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

# max of 1 log as txt at max 1MB
# creates path and file if not created already
handler = RotatingFileHandler(
    "logs/log.txt", maxBytes=1024 * 1024, backupCount=1, encoding="utf-8"
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | [%(levelname)s] | %(message)s",
    handlers=[handler],
)

logger = logging.getLogger(__name__)

logger.info("\n")

logger.info("Logger online!")
