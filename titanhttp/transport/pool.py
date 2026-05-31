import time
import threading
from collections import deque
from typing import Dict, Optional
import socket
from ..types import ConnectionMetadata


class PooledConnection:
    def __init__(self, sock: socket.socket, protocol: str = "http/1.1"):
        self.sock = sock
        self.meta = ConnectionMetadata(created_at=time.time(), protocol=protocol)

    def is_usable(self, idle_timeout: float = 30.0, max_lifetime: float = 300.0) -> bool:
        if self.meta.idle_time > idle_timeout:
            return False
        if self.meta.age > max_lifetime:
            return False
        try:
            # Check if socket is still alive
            self.sock.settimeout(0)
            peek = self.sock.recv(1, socket.MSG_PEEK)
            self.sock.settimeout(30)
            return True
        except BlockingIOError:
            self.sock.settimeout(30)
            return True
        except Exception:
            return False

    def mark_used(self):
        self.meta.last_used = time.time()
        self.meta.request_count += 1
        self.meta.idle = False

    def mark_idle(self):
        self.meta.idle = True


class ConnectionPool:
    def __init__(self, max_per_host: int = 10, idle_timeout: float = 30.0, max_lifetime: float = 300.0):
        self.max_per_host = max_per_host
        self.idle_timeout = idle_timeout
        self.max_lifetime = max_lifetime
        self._pools: Dict[str, deque] = {}
        self._lock = threading.Lock()

    def _origin(self, scheme: str, host: str, port: int) -> str:
        return f"{scheme}://{host}:{port}"

    def get(self, scheme: str, host: str, port: int) -> Optional[PooledConnection]:
        origin = self._origin(scheme, host, port)
        with self._lock:
            pool = self._pools.get(origin)
            if not pool:
                return None
            while pool:
                conn = pool.pop()
                if conn.is_usable(self.idle_timeout, self.max_lifetime):
                    conn.mark_used()
                    return conn
                else:
                    self._close(conn)
            return None

    def put(self, scheme: str, host: str, port: int, conn: PooledConnection):
        origin = self._origin(scheme, host, port)
        with self._lock:
            if origin not in self._pools:
                self._pools[origin] = deque()
            if len(self._pools[origin]) >= self.max_per_host:
                self._close(self._pools[origin].popleft())
            conn.mark_idle()
            self._pools[origin].append(conn)

    def _close(self, conn: PooledConnection):
        try:
            conn.sock.close()
        except Exception:
            pass

    def close_all(self):
        with self._lock:
            for pool in self._pools.values():
                for conn in pool:
                    self._close(conn)
            self._pools.clear()
