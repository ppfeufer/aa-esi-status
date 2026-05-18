"""
Cache handler for AA ESI Status.
"""

# Standard Library
from datetime import timedelta
from typing import Any

# Django
from django.core.cache import cache
from django.utils.timezone import now

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA ESI Status
from esistatus import __title__
from esistatus.providers.applogger import AppLogger

logger = AppLogger(my_logger=get_extension_logger(__name__), prefix=__title__)


class Cache:
    """
    Handling the redis cache for AA ESI Status.
    """

    redis_key_base = "esi:meta"

    def __init__(self, subkey: str) -> None:
        """
        Initialize the Cache with a subkey.

        :param subkey: The subkey to use for caching.
        :type subkey: string
        """

        if not isinstance(subkey, str):
            raise TypeError("Argument 'subkey' must be a string")

        if not subkey.strip():
            raise ValueError("Argument 'subkey' must be a non-empty string")

        self.subkey = subkey

    def _get_cache_key(self) -> str:
        """
        Generate a cache key based on the URL.

        :return: The full cache key.
        :rtype: string
        """

        cache_key = f"{self.redis_key_base}:{self.subkey}"

        logger.debug(f"Generating cache key for: {cache_key}")

        return cache_key

    @staticmethod
    def _get_max_cache_time() -> int:
        """
        Get the maximum cache time until 11:30 AM (UTC) the next day.

        :return: The maximum cache time until 11:30 AM (UTC) the next day.
        :rtype: integer
        """

        expire_time = now()
        target = expire_time.replace(hour=11, minute=30, second=0, microsecond=0)

        if expire_time >= target:
            target += timedelta(days=1)

        return int((target - expire_time).total_seconds())

    def set(self, value: Any) -> None:
        """
        Set a specific cache value for a URL.

        :param value: The value to cache.
        :type value: Any
        :return: None
        :rtype: None
        """

        cache_key = self._get_cache_key()

        logger.debug(f"Setting cache for: {cache_key}")

        cache.set(
            key=cache_key,
            value=value,
            timeout=self._get_max_cache_time(),
        )

    def get(self) -> Any:
        """
        Get a specific cache value for a URL.

        :return: The cached value for a cache key, or False if not found.
        :rtype: Any
        """

        cache_key = self._get_cache_key()

        logger.debug(f"Getting cache for: {cache_key}")

        return cache.get(key=cache_key, default=False)
