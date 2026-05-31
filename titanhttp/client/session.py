from typing import Dict, Optional
from .cookie.jar import CookieJar
from .cache.manager import CacheManager


class SessionState:
    def __init__(self, cookie_jar: Optional[CookieJar] = None, cache: Optional[CacheManager] = None):
        self.cookie_jar = cookie_jar or CookieJar()
        self.cache = cache

    def apply_cookies(self, host: str, path: str, headers: Dict[str, str]):
        cookie_str = self.cookie_jar.get_cookie_header(host, path)
        if cookie_str:
            headers["Cookie"] = cookie_str

    def store_cookies(self, host: str, set_cookie_headers: list):
        for sc in set_cookie_headers:
            self.cookie_jar.set_cookie(host, sc)
