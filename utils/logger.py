import logging
from datetime import datetime
from pydantic import BaseModel
import json
from contextvars import ContextVar

class RequestContextVar(BaseModel):
    request_id: str
    request_path: str
    
    
request_ctx_var: ContextVar[RequestContextVar|None] = ContextVar(
    "request_ctx_var", default=None
)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        ctx=request_ctx_var.get()
        log_record={
            "timestamp":datetime.now().isoformat(),
            "level":record.levelname,
            "request_id": ctx.request_id if ctx else None,
            "request_path": ctx.request_path if ctx else None,
            "logger":record.name,
            "message":record.getMessage(),
            "filename":record.flename(),
            "line":record.lineno
        }
        return json.dumps(log_record)
    
    
def get_logger(name:str):
    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler= logging.FileHandler(f"{name}.log")
    handler.setFormatter(JsonFormatter())
    return logger