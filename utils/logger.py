import logging
from datetime import datetime
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record={
            "timestamp":datetime.now().isoformat(),
            "level":record.levelname,
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