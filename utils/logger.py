import logging
import datetime
import json




class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "filename": record.filename,
            "line": record.lineno
        }
        return json.dumps(log_record)
    
def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(f"{name}.log")
    handler.setFormatter(JsonFormatter())

    logger.addHandler(handler)

    return logger
