import json
import logging
from contextvars import ContextVar
from datetime import datetime

from pydantic import BaseModel


class RequestContextVar(BaseModel):
    request_id: str
    request_path: str


request_ctx_var: ContextVar[RequestContextVar | None] = ContextVar(
    "request_ctx_var", default=None
)

__logger: logging.Logger | None = None


class JsonFormatter(logging.Formatter):
    def format(self, record):
        ctx = request_ctx_var.get()
        log_record = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "request_id": ctx.request_id if ctx else None,
            "request_path": ctx.request_path if ctx else None,
            "logger": record.name,
            "message": record.getMessage(),
            "line": record.lineno,
        }
        return json.dumps(log_record)


def get_logger() -> logging.Logger:
    global __logger
    if __logger:
        return __logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    __logger = logger
    return logger
