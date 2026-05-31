import time
from typing import Dict, Optional, Tuple
from collections import OrderedDict


class MemoryCache:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._store: OrderedDict[str, Tuple[dict, float]] = OrderedDict()

    def get(self, key: str) -> Optional[dict]:
        if key in self._store:
            entry, expiry = self._store[key]
            if expiry > time.time():
                self._store.move_to_end(key)
                return entry
            else:
                del self._store[key]
        return None

    def set(self, key: str, entry: dict, ttl: float):
        if len(self._store) >= self.max_size:
            self._store.popitem(last=False)
        self._store[key] = (entry, time.time() + ttl)
        self._store.move_to_end(key)

    def invalidate(self, key: str):
        self._store.pop(key, None)

    def clear(self):
        self._store.clear()
