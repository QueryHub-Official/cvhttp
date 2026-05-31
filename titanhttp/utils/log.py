import json
import sys
from datetime import datetime


class Logger:
    @staticmethod
    def trace(event: str, **kwargs):
        log = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            **kwargs,
        }
        sys.stderr.write(json.dumps(log, default=str) + "\n")
