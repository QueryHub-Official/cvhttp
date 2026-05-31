import time
import random
import threading
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ProxyEntry:
    url: str
    weight: float = 1.0
    fail_count: int = 0
    last_used: float = 0.0
    disabled_until: float = 0.0
    avg_latency: float = 0.0


class ProxyRotator:
    def __init__(self, proxies: List[str], health_check_url: Optional[str] = None):
        self.proxies = [ProxyEntry(url=p) for p in proxies]
        self.health_check_url = health_check_url
        self._lock = threading.Lock()

    def get_proxy(self) -> Optional[str]:
        with self._lock:
            now = time.time()
            available = [p for p in self.proxies if p.disabled_until < now]
            if not available:
                return None
            total = sum(p.weight for p in available)
            r = random.uniform(0, total)
            cumulative = 0
            for p in available:
                cumulative += p.weight
                if r <= cumulative:
                    p.last_used = now
                    return p.url
            return available[-1].url

    def report_success(self, proxy_url: str, latency: float):
        with self._lock:
            for p in self.proxies:
                if p.url == proxy_url:
                    p.fail_count = max(0, p.fail_count - 1)
                    p.avg_latency = 0.7 * p.avg_latency + 0.3 * latency
                    break

    def report_failure(self, proxy_url: str):
        with self._lock:
            for p in self.proxies:
                if p.url == proxy_url:
                    p.fail_count += 1
                    if p.fail_count >= 3:
                        p.disabled_until = time.time() + 60
                    break
