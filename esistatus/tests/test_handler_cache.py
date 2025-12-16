# Standard Library
from unittest.mock import patch

# Django
from django.utils.datetime_safe import datetime
from django.utils.timezone import make_aware, now

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
    """
    Test the _get_max_cache_time function.
    """

    def test_returns_seconds_until_1130_am_next_day(self):
        """
        Test that the function returns the correct number of seconds until 11:30 AM the next day.

        :return:
        :rtype:
        """

        with patch("esistatus.handler.cache.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2023, 10, 1, 10, 0, 0))

            result = _get_max_cache_time()

            self.assertEqual(result, 5400)

    def test_returns_seconds_until_1130_am_same_day(self):
        """
        Test that the function returns the correct number of seconds until 11:30 AM the same day.

        :return:
        :rtype:
        """

        with patch("esistatus.handler.cache.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2023, 10, 1, 9, 0, 0))

            result = _get_max_cache_time()

            self.assertEqual(result, 9000)

    def test_handles_time_after_1130_am_next_day_interval(self):
        """
        Test that times after 11:30 AM return the correct interval until 11:30 AM the next day.

        :return:
        :rtype:
        """

        with patch("esistatus.handler.cache.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2023, 10, 1, 12, 0, 0))

            result = _get_max_cache_time()

            self.assertEqual(result, 84600)

    def test_handles_time_exactly_at_1130_am_results_in_full_day(self):
        """
        Test that exactly 11:30 AM returns a full day's seconds until the next 11:30 AM.

        :return:
        :rtype:
        """

        with patch("esistatus.handler.cache.now") as mock_now:
            mock_now.return_value = make_aware(datetime(2023, 10, 1, 11, 30, 0))

            result = _get_max_cache_time()

            self.assertEqual(result, 86400)

    def test_handles_midnight_boundary_correctly(self):
        """
        Test that the midnight boundary is handled correctly.

        :return:
        :rtype:
        """

        current_time = now().replace(hour=0, minute=0, second=0, microsecond=0)
        expected_expiry = current_time.replace(hour=11, minute=30, second=0)

        with patch("esistatus.handler.cache.now", return_value=current_time):
            result = _get_max_cache_time()

            self.assertEqual(
                result, int((expected_expiry - current_time).total_seconds())
            )
