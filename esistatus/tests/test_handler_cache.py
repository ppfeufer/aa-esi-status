# Standard Library
import datetime as dt
from unittest.mock import patch

# Django
from django.utils.timezone import now

# AA ESI Status
from esistatus.handler.cache import (
    _get_cache,
    _get_cache_key,
    _get_max_cache_time,
    _set_cache,
)
from esistatus.tests import BaseTestCase


class TestHelperGetCache(BaseTestCase):
    """
    Test the _get_cache function.
    """

    def test_retrieves_cached_value_when_key_exists(self):
        """
        Test retrieving a cached value when the key exists.

        :return:
        :rtype:
        """

        url = "https://example.com/api"
        cache_key = "ESI_META_CACHE_12345"
        cached_value = {"data": "cached_data"}

        with (
            patch("esistatus.handler.cache.cache.get") as mock_cache_get,
            patch(
                "esistatus.handler.cache._get_cache_key",
                return_value=cache_key,
            ),
        ):
            mock_cache_get.return_value = cached_value

            result = _get_cache(url)

            self.assertEqual(result, cached_value)
            mock_cache_get.assert_called_once_with(cache_key, False)

    def test_returns_false_when_key_does_not_exist(self):
        """
        Test returning False when the cache key does not exist.

        :return:
        :rtype:
        """

        url = "https://example.com/api"
        cache_key = "ESI_META_CACHE_12345"

        with (
            patch("esistatus.handler.cache.cache.get") as mock_cache_get,
            patch(
                "esistatus.handler.cache._get_cache_key",
                return_value=cache_key,
            ),
        ):
            mock_cache_get.return_value = False

            result = _get_cache(url)

            self.assertFalse(result)
            mock_cache_get.assert_called_once_with(cache_key, False)


class TestHelperSetCache(BaseTestCase):
    """
    Test the _set_cache function.
    """

    def test_sets_cache_value_with_correct_key_and_expiry(self):
        """
        Test setting a cache value with the correct key and expiry.

        :return:
        :rtype:
        """

        url = "https://example.com/api"
        value = {"data": "test_data"}
        cache_key = "ESI_META_CACHE_12345"
        max_cache_time = 3600

        with (
            patch("esistatus.handler.cache.cache.set") as mock_cache_set,
            patch("esistatus.handler.cache._get_cache_key", return_value=cache_key),
            patch(
                "esistatus.handler.cache._get_max_cache_time",
                return_value=max_cache_time,
            ),
        ):
            _set_cache(url, value)

            mock_cache_set.assert_called_once_with(cache_key, value, max_cache_time)

    def test_does_not_fail_when_setting_cache_with_empty_value(self):
        """
        Test that setting a cache with an empty value does not fail.

        :return:
        :rtype:
        """

        url = "https://example.com/api"
        value = None
        cache_key = "ESI_META_CACHE_12345"
        max_cache_time = 3600

        with (
            patch("esistatus.handler.cache.cache.set") as mock_cache_set,
            patch("esistatus.handler.cache._get_cache_key", return_value=cache_key),
            patch(
                "esistatus.handler.cache._get_max_cache_time",
                return_value=max_cache_time,
            ),
        ):
            _set_cache(url, value)

            mock_cache_set.assert_called_once_with(cache_key, value, max_cache_time)


class TestHelperGetCacheKey(BaseTestCase):
    """
    Test the _get_cache_key function.
    """

    def test_generates_consistent_cache_key_for_same_url(self):
        """
        Test that the same URL generates the same cache key.

        :return:
        :rtype:
        """

        url = "https://example.com/api/resource"

        result1 = _get_cache_key(url)
        result2 = _get_cache_key(url)

        self.assertEqual(result1, result2)

    def test_generates_different_cache_keys_for_different_urls(self):
        """
        Test that different URLs generate different cache keys.

        :return:
        :rtype:
        """

        url1 = "https://example.com/api/resource1"
        url2 = "https://example.com/api/resource2"

        result1 = _get_cache_key(url1)
        result2 = _get_cache_key(url2)

        self.assertNotEqual(result1, result2)

    def test_handles_empty_url_gracefully(self):
        """
        Test that an empty URL is handled gracefully.

        :return:
        :rtype:
        """

        url = ""

        result = _get_cache_key(url)

        self.assertTrue(result.startswith("ESI_META_CACHE_"))
        self.assertGreater(len(result), len("ESI_META_CACHE_"))


class TestHelperGetMaxCacheTime(BaseTestCase):
    def test_calculates_correct_cache_time_before_1130_am(self):
        """
        Test that the correct cache time is calculated before 11:30 AM.

        :return:
        :rtype:
        """

        current_time = now().replace(hour=10, minute=0, second=0, microsecond=0)
        expected_expiry = current_time.replace(hour=11, minute=30, second=0)

        with patch(
            "esistatus.handler.cache.timezone.now",
            return_value=current_time,
        ):
            result = _get_max_cache_time()

            self.assertEqual(
                result, int((expected_expiry - current_time).total_seconds())
            )

    def test_calculates_correct_cache_time_after_1130_am(self):
        """
        Test that the correct cache time is calculated after 11:30 AM.

        :return:
        :rtype:
        """

        current_time = now().replace(hour=12, minute=0, second=0, microsecond=0)
        expected_expiry = (current_time + dt.timedelta(days=1)).replace(
            hour=11, minute=30, second=0
        )

        with patch(
            "esistatus.handler.cache.timezone.now",
            return_value=current_time,
        ):
            result = _get_max_cache_time()

            self.assertEqual(
                result, int((expected_expiry - current_time).total_seconds())
            )

    def test_handles_midnight_boundary_correctly(self):
        """
        Test that the midnight boundary is handled correctly.

        :return:
        :rtype:
        """

        current_time = now().replace(hour=0, minute=0, second=0, microsecond=0)
        expected_expiry = current_time.replace(hour=11, minute=30, second=0)

        with patch(
            "esistatus.handler.cache.timezone.now",
            return_value=current_time,
        ):
            result = _get_max_cache_time()

            self.assertEqual(
                result, int((expected_expiry - current_time).total_seconds())
            )
