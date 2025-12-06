from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pythonjsonlogger import orjson

if TYPE_CHECKING:
    from typing import Any

RESERVED_LOG_FIELDS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "asctime",
}


class KeyValueLogFormatter(logging.Formatter):
    """
    Formats logs with a timestamp prefix followed by key=value pairs.
    Example: [2025-11-23T12:27:00] INFO     myapp                            User logged in user_id=42
    """

    def __init__(self, datefmt="%Y-%m-%dT%H:%M:%S"):
        format_string = "[%(asctime)s] %(levelname)-8s %(name)-40s %(message)s"
        super().__init__(fmt=format_string, datefmt=datefmt)

    def format(self, record):
        if kv_pairs := [
            f"{key}={self._format_value(value)}"
            for key, value in record.__dict__.items()
            if key not in RESERVED_LOG_FIELDS and value is not None
        ]:
            record.msg = f"{record.msg} {' '.join(kv_pairs)}"

        result = super().format(record)

        # Add exception info if present
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if result[-1:] != "\n":
                result = result + "\n"
            result = result + record.exc_text

        return result

    def _format_value(self, value: Any) -> str:
        value_str = str(value)
        if " " in value_str or "=" in value_str or '"' in value_str:
            clean_str = value_str.replace('"', '"')
            return f'"{clean_str}"'
        return value_str


def setup_logger(level=logging.INFO, log_format="kv"):
    handler = logging.StreamHandler()
    if log_format == "json":
        handler.setFormatter(orjson.OrjsonFormatter)
    else:
        handler.setFormatter(KeyValueLogFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def get_logger(name=None):
    return logging.getLogger(name)
