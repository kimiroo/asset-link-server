import logging
from src.core.config import get_settings

settings = get_settings()


class ColoredFormatter(logging.Formatter):
    """Custom formatter to inject ANSI color codes into log levels."""

    ansi_colors = {
        logging.DEBUG: "\x1b[36m",    # Cyan
        logging.INFO: "\x1b[32m",     # Green
        logging.WARNING: "\x1b[33m",  # Yellow
        logging.ERROR: "\x1b[31m",    # Red
        logging.CRITICAL: "\x1b[41m", # Red background
    }
    reset_code = "\x1b[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.ansi_colors.get(record.levelno, self.reset_code)
        orig_levelname = record.levelname
        record.levelname = f"{color}{orig_levelname}{self.reset_code}"
        result = super().format(record)
        record.levelname = orig_levelname
        return result


def setup_logging() -> None:
    """Configure root logger and redirect Uvicorn logs."""
    log_format = "%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
    time_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(ColoredFormatter(fmt=log_format, datefmt=time_format))
    root_logger.addHandler(stream_handler)

    # Force Uvicorn to use the root logger configuration
    for uvicorn_logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True