import os
import os.path
import logging
import logging.handlers
from dotenv import load_dotenv
from .constants import LOG_LEVELS

load_dotenv()

STREAM_LOG_LEVEL = os.environ.get("STREAM_LOG_LEVEL")
FILE_BACKUP_COUNT = os.environ.get("FILE_BACKUP_COUNT")
LOG_ROTATION_TIME = os.environ.get("LOG_ROTATION_TIME")
LOGS_DIRECTORY=os.environ.get("LOGS_DIRECTORY")

logging.getLogger("urllib3").propagate = False

log_formatter = "[%(levelname)s] (%(asctime)s) %(message)s"
date_formatter = "%Y-%m-%d %H:%M:%S"

def _format_log_paths(directory=LOGS_DIRECTORY, levels=LOG_LEVELS):
  for name, path in LOG_LEVELS.items():
    path = os.path.join(directory, path)
    levels[name] = path

  return levels

def create_logger(name="git-sync", directory=LOGS_DIRECTORY, levels=LOG_LEVELS):
  logger = logging.getLogger(name)
  levels = _format_log_paths(directory, levels)

  for level, path in levels.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    formatter = logging.Formatter(log_formatter, date_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(getattr(logging, STREAM_LOG_LEVEL, "INFO"))
    stream_handler.setFormatter(formatter)

    file_handler = logging.handlers.TimedRotatingFileHandler(
      filename=path,
      when=LOG_ROTATION_TIME if LOG_ROTATION_TIME else "midnight",
      backupCount=int(FILE_BACKUP_COUNT) if FILE_BACKUP_COUNT else 30
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, level))
    logger.addHandler(file_handler)

  return logger
