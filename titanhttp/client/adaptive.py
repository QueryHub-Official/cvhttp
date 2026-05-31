import time
import statistics
from typing import Dict, List


class AdaptiveTimeout:
    def __init__(self, window: int = 100):
        self.window = window
        self._history: Dict[str, List[float]] = {}

    def record(self, host: str, elapsed: float):
        if host not in self._history:
            self._history[host] = []
        self._history[host].append(elapsed)
        if len(self._history[host]) > self.window:
            self._history[host].pop(0)

    def timeout_for(self, host: str, default: float) -> float:
        times = self._history.get(host, [])
        if len(times) < 5:
            return default
        p95 = statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times)
        return max(5.0, min(p95 * 3, 120.0, default * 2))
