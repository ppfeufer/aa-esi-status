"""
Cache handler for AA ESI Status component.
"""

# Standard Library
from datetime import timedelta
from hashlib import md5
from typing import Any

# Django
from django.core.cache import cache
from django.utils.timezone import now


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


def _get_cache_key(url: str) -> str:
    """
    Generate a cache key based on the URL.

    :param url:
    :type url:
    :return:
    :rtype:
    """

    return "ESI_META_CACHE_" + md5(url.encode("utf-8")).hexdigest()


def _set_cache(url: str, value: Any) -> None:
    """
    Set a specific cache value for a URL.

    :param url:
    :type url:
    :param value:
    :type value:
    :return:
    :rtype:
    """

    cache.set(_get_cache_key(url), value, _get_max_cache_time())


def _get_cache(url: str) -> Any:
    """
    Get a specific cache value for a URL.

    :param url:
    :type url:
    :return:
    :rtype:
    """

    return cache.get(_get_cache_key(url), False)
