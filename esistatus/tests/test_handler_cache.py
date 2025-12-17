# Standard Library
from unittest import mock

# Django
from django.utils.crypto import md5
from django.utils.datetime_safe import datetime

# AA ESI Status
from esistatus.handler.cache import Cache
from esistatus.tests import BaseTestCase


class TestCacheClassInit(BaseTestCase):
    """
    Test the Cache class initialization.
    """

    def test_initializes_with_valid_subkey(self):
        """
        Test initializing the Cache class with a valid subkey.

        :return:
        :rtype:
        """

        with mock.patch("esistatus.handler.cache.cache"):
            cache_instance = Cache(subkey="test_subkey")

            self.assertEqual(cache_instance.subkey, "test_subkey")

    def test_raises_type_error_when_initialized_with_non_string_subkey(self):
        """
        Test that initializing the Cache class with a non-string subkey raises a TypeError.

        :return:
        :rtype:
        """

        with self.assertRaises(TypeError):
            Cache(subkey=12345)

    def test_raises_value_error_when_initialized_with_empty_subkey(self):
        """
        Test that initializing the Cache class with an empty subkey raises a ValueError.

        :return:
        :rtype:
        """

        with self.assertRaises(ValueError):
            Cache(subkey="")

    def test_raises_value_error_when_initialized_with_whitespace_subkey(self):
        """
        Test that initializing the Cache class with a whitespace-only subkey raises a ValueError.

        :return:
        :rtype:
        """

        with self.assertRaises(ValueError):
            Cache(subkey="   ")

    def test_rasies_value_error_with_none_subkey(self):
        """
        Test that initializing the Cache class with a None subkey raises a ValueError.

        :return:
        :rtype:
        """

        with self.assertRaises(TypeError):
            Cache(subkey=None)

    def test_rasies_type_error_with_no_subkey(self):
        """
        Test that initializing the Cache class without providing the required subkey raises a TypeError.

        :return:
        :rtype:
        """

        with self.assertRaises(TypeError):
            Cache()


class TestHelperGetCache(BaseTestCase):
    """
    Test the Cache.get function.
    """

    def test_retrieves_cached_value_for_valid_url(self):
        """
        Test retrieving a cached value for a valid URL.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_subkey")
        url = "https://example.com/resource"
        expected_value = {"data": "test_value"}

        with mock.patch(
            "esistatus.handler.cache.cache.get", return_value=expected_value
        ) as mock_get:
            result = cache_instance.get(url)

            self.assertEqual(result, expected_value)
            mock_get.assert_called_once_with(
                key=cache_instance._get_cache_key(url=url), default=False
            )

    def test_returns_false_for_nonexistent_cache_key(self):
        """
        Test returning False for a nonexistent cache key.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_subkey")
        url = "https://example.com/nonexistent"

        with mock.patch(
            "esistatus.handler.cache.cache.get", return_value=False
        ) as mock_get:
            result = cache_instance.get(url)

            self.assertFalse(result)
            mock_get.assert_called_once_with(
                key=cache_instance._get_cache_key(url=url), default=False
            )

    def test_raises_value_error_when_getting_cache_with_empty_url(self):
        """
        Test that getting a cache with an empty URL raises a ValueError.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_subkey")

        with self.assertRaises(ValueError):
            cache_instance.get("")

    def test_raises_type_error_when_getting_cache_with_non_string_url(self):
        """
        Test that getting a cache with a non-string URL raises a TypeError.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_subkey")

        with self.assertRaises(TypeError):
            cache_instance.get(12345)


class TestHelperSetCache(BaseTestCase):
    """
    Test the Cache.set function.
    """

    def test_sets_cache_with_correct_key_and_value(self):
        """
        Test setting a cache value with the correct key and value.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_subkey")
        url = "https://example.com/resource"
        value = {"data": "test_value"}

        with mock.patch("esistatus.handler.cache.cache.set") as mock_set:
            cache_instance.set(url, value)

            mock_set.assert_called_once_with(
                key=cache_instance._get_cache_key(url),
                value=value,
                timeout=cache_instance._get_max_cache_time(),
            )

    def test_raises_value_error_when_setting_cache_with_empty_url(self):
        """
        Test that setting a cache with an empty URL raises a ValueError.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_subkey")

        with self.assertRaises(ValueError):
            cache_instance.set("", {"data": "test_value"})

    def test_raises_type_error_when_setting_cache_with_non_string_url(self):
        """
        Test that setting a cache with a non-string URL raises a TypeError.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_subkey")

        with self.assertRaises(TypeError):
            cache_instance.set(12345, {"data": "test_value"})


class TestHelperGetCacheKey(BaseTestCase):
    """
    Test the Cache._get_cache_key function.
    """

    def test_generates_correct_cache_key_with_valid_url(self):
        """
        Test that a valid URL generates the correct cache key.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_subkey")
        url = "https://example.com/resource"

        expected_key = f"esi:meta:test_subkey:{md5(url.encode()).hexdigest()}"

        self.assertEqual(cache_instance._get_cache_key(url), expected_key)

    def test_raises_attribute_error_with_non_string_url(self):
        """
        Test that providing a non-string URL raises an AttributeError.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_subkey")

        with self.assertRaises(AttributeError):
            cache_instance._get_cache_key(12345)

    def test_generates_different_keys_for_different_urls(self):
        """
        Test that different URLs generate different cache keys.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_subkey")

        url1 = "https://example.com/resource1"
        url2 = "https://example.com/resource2"

        self.assertNotEqual(
            cache_instance._get_cache_key(url1), cache_instance._get_cache_key(url2)
        )

    def test_generates_different_keys_for_different_subkeys(self):
        """
        Test that different subkeys generate different cache keys for the same URL.

        :return:
        :rtype:
        """

        cache_instance1 = Cache(subkey="subkey1")
        cache_instance2 = Cache(subkey="subkey2")

        url = "https://example.com/resource"

        self.assertNotEqual(
            cache_instance1._get_cache_key(url), cache_instance2._get_cache_key(url)
        )


class TestHelperGetMaxCacheTime(BaseTestCase):
    """
    Test the Cache._get_max_cache_time function.
    """

    def test_calculates_correct_cache_time_before_target(self):
        """
        Test that the function calculates the correct number of seconds until 11:30 AM the same day.

        :return:
        :rtype:
        """

        with mock.patch("esistatus.handler.cache.now") as mock_now:
            mock_now.return_value = datetime(2023, 10, 1, 10, 0, 0)

            result = Cache._get_max_cache_time()

            self.assertEqual(result, 5400)  # 1.5 hours in seconds

    def test_calculates_correct_cache_time_after_target(self):
        """
        Test that the function calculates the correct number of seconds until 11:30 AM the next day.

        :return:
        :rtype:
        """

        with mock.patch("esistatus.handler.cache.now") as mock_now:
            mock_now.return_value = datetime(2023, 10, 1, 12, 0, 0)

            result = Cache._get_max_cache_time()

            self.assertEqual(result, 84600)  # 23.5 hours in seconds

    def test_calculates_correct_cache_time_at_target(self):
        """
        Test that the function calculates the correct number of seconds when the time is exactly 11:30 AM.

        :return:
        :rtype:
        """

        with mock.patch("esistatus.handler.cache.now") as mock_now:
            mock_now.return_value = datetime(2023, 10, 1, 11, 30, 0)

            result = Cache._get_max_cache_time()

            self.assertEqual(result, 86400)  # 24 hours in seconds
