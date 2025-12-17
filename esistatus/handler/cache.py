"""
Cache handler for AA ESI Status.
"""

# Standard Library
from datetime import timedelta
from typing import Any

# Django
from django.core.cache import cache
from django.utils.crypto import md5
from django.utils.timezone import now

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA ESI Status
from esistatus import __title__
from esistatus.providers import AppLogger

logger = AppLogger(my_logger=get_extension_logger(__name__), prefix=__title__)


class Cache:
    """
    Handling the redis cache for AA ESI Status.
    """

    redis_key_base = "esi:meta"

    def __init__(self, subkey: str) -> None:
        """
        Initialize the Cache with a subkey.

        :param subkey:
        :type subkey:
        """

        if not isinstance(subkey, str):
            raise TypeError("Argument 'subkey' must be a string")

        if not subkey.strip():
            raise ValueError("Argument 'subkey' must be a non-empty string")

        self.subkey = subkey

    def _get_cache_key(self, url: str) -> str:
        """
        Generate a cache key based on the URL.

        :param url:
        :type url:
        :return:
        :rtype:
        """

        logger.debug(f"Generating cache key for URL: {url}")

        return f"{self.redis_key_base}:{self.subkey}:{md5(url.encode()).hexdigest()}"

    @staticmethod
    def _get_max_cache_time() -> int:
        """
        Get the maximum cache time until 11:30 AM the next day.

        :return:
        :rtype:
        """

        expire_time = now()
        target = expire_time.replace(hour=11, minute=30, second=0, microsecond=0)

        if expire_time >= target:
            target += timedelta(days=1)

        return int((target - expire_time).total_seconds())

    def set(self, url: str, value: Any) -> None:
        """
        Set a specific cache value for a URL.

        :param url:
        :type url:
        :param value:
        :type value:
        :return:
        :rtype:
        """

        logger.debug(f"Setting cache for URL: {url}")

        if not isinstance(url, str):
            raise TypeError("Argument 'url' must be a string")

        if not url.strip():
            raise ValueError("Argument 'url' must be a non-empty string")

        cache.set(
            key=self._get_cache_key(url),
            value=value,
            timeout=self._get_max_cache_time(),
        )

    def get(self, url: str) -> Any:
        """
        Get a specific cache value for a URL.

        :param url:
        :type url:
        :return:
        :rtype:
        """

        logger.debug(f"Getting cache for URL: {url}")

        if not isinstance(url, str):
            raise TypeError("Argument 'url' must be a string")

        if not url.strip():
            raise ValueError("Argument 'url' must be a non-empty string")

        return cache.get(key=self._get_cache_key(url=url), default=False)
