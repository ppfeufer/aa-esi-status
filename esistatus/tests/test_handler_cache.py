# Standard Library
from unittest import mock

# Django
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


class TestCacheGet(BaseTestCase):
    """
    Test the Cache.get function.
    """

    def test_retrieves_value_from_cache(self):
        """
        Test that the function retrieves the correct value from the cache.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_key")
        mock_cache_key = cache_instance._get_cache_key()
        mock_value = "test_value"

        with mock.patch(
            "django.core.cache.cache.get", return_value=mock_value
        ) as mock_get:
            result = cache_instance.get()

            mock_get.assert_called_once_with(key=mock_cache_key, default=False)
            self.assertEqual(result, mock_value)

    def test_returns_false_when_cache_is_empty(self):
        """
        Test that the function returns False when the cache is empty.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_key")
        mock_cache_key = cache_instance._get_cache_key()

        with mock.patch("django.core.cache.cache.get", return_value=False) as mock_get:
            result = cache_instance.get()

            mock_get.assert_called_once_with(key=mock_cache_key, default=False)
            self.assertFalse(result)


class TestCacheSet(BaseTestCase):
    """
    Test the Cache.set function.
    """

    def test_sets_cache_value_with_correct_key_and_timeout(self):
        """
        Test that the function sets the cache value with the correct key and timeout.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="test_key")
        mock_cache_key = cache_instance._get_cache_key()
        mock_value = "test_value"
        mock_timeout = 3600

        with (
            mock.patch("django.core.cache.cache.set") as mock_set,
            mock.patch.object(Cache, "_get_max_cache_time", return_value=mock_timeout),
        ):
            cache_instance.set(mock_value)

            mock_set.assert_called_once_with(
                key=mock_cache_key, value=mock_value, timeout=mock_timeout
            )

    def test_raises_type_error_when_subkey_is_not_string(self):
        """
        Test that providing a non-string subkey raises a TypeError.

        :return:
        :rtype:
        """

        with self.assertRaises(TypeError):
            Cache(subkey=123)

    def test_raises_value_error_when_subkey_is_empty(self):
        """
        Test that providing an empty subkey raises a ValueError.

        :return:
        :rtype:
        """

        with self.assertRaises(ValueError):
            Cache(subkey="   ")


class TestCacheHelperGetCacheKey(BaseTestCase):
    """
    Test the Cache._get_cache_key function.
    """

    def test_generates_cache_key_with_valid_subkey(self):
        """
        Test that a valid subkey generates the correct cache key.

        :return:
        :rtype:
        """

        cache_instance = Cache(subkey="valid-subkey")
        result = cache_instance._get_cache_key()

        self.assertEqual(result, "esi:meta:valid-subkey")

    def test_raises_type_error_when_subkey_is_not_string_in_key_generation(self):
        """
        Test that providing a non-string subkey raises a TypeError.

        :return:
        :rtype:
        """

        with self.assertRaises(TypeError):
            Cache(subkey=123)._get_cache_key()

    def test_raises_value_error_when_subkey_is_empty_in_key_generation(self):
        """
        Test that providing an empty subkey raises a ValueError.

        :return:
        :rtype:
        """

        with self.assertRaises(ValueError):
            Cache(subkey="   ")._get_cache_key()


class TestCacheHelperGetMaxCacheTime(BaseTestCase):
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
