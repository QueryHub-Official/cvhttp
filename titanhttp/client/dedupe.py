import threading
import hashlib
import time
from typing import Dict, Optional, Any


class DedupeManager:
    def __init__(self, ttl: float = 5.0):
        self.ttl = ttl
        self._inflight: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def _key(self, method: str, url: str, body: Optional[bytes]) -> str:
        parts = [method, url]
        if body:
            parts.append(hashlib.sha256(body).hexdigest()[:16])
        return hashlib.sha256("|".join(parts).encode()).hexdigest()

    def check(self, method: str, url: str, body: Optional[bytes]) -> Optional[Any]:
        key = self._key(method, url, body)
        with self._lock:
            return self._inflight.get(key)

    def store(self, method: str, url: str, body: Optional[bytes], response: Any):
        key = self._key(method, url, body)
        with self._lock:
            self._inflight[key] = response
        threading.Timer(self.ttl, lambda: self._remove(key)).start()

    def _remove(self, key: str):
        with self._lock:
            self._inflight.pop(key, None)
