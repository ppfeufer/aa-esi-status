# Standard Library
import json
from unittest.mock import Mock, patch

# Third Party
import requests

# AA ESI Status
from esistatus.tasks import (
    _get_esi_status_json,
    _get_latest_compatibility_date,
    _get_openapi_specs_json,
    update_esi_status,
)
from esistatus.tests import BaseTestCase


class TestHelperGetLatestCompatibilityDate(BaseTestCase):
    """
    Test the _get_latest_compatibility_date function.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.compatibility_date_json = {
            "compatibility_dates": [
                "2025-11-06",
                "2025-09-30",
                "2025-09-26",
                "2025-08-26",
                "2020-01-01",
            ]
        }
        cls.latest_date = "2025-11-06"

    def test_returns_latest_date_from_cache(self):
        """
        Test returning the latest compatibility date from cache.

        :return:
        :rtype:
        """

        with patch(
            "esistatus.tasks.cache_handler._get_cache", return_value=self.latest_date
        ) as mock_cache:
            result = _get_latest_compatibility_date()

            self.assertEqual(result, self.latest_date)
            mock_cache.assert_called_once()

    def test_fetches_latest_date_and_caches_when_cache_is_empty(self):
        """
        Test fetching the latest compatibility date and caching it when the cache is empty.

        :return:
        :rtype:
        """

        with (
            patch("esistatus.tasks.cache_handler._get_cache", return_value=None),
            patch("esistatus.tasks.requests.get") as mock_get,
            patch("esistatus.tasks.cache_handler._set_cache") as mock_set_cache,
        ):
            mock_response = Mock()
            mock_response.json.return_value = self.compatibility_date_json
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = _get_latest_compatibility_date()

            self.assertEqual(result, self.latest_date)
            mock_get.assert_called_once()
            mock_set_cache.assert_called_once()

    def test_returns_none_when_no_valid_dates_are_present(self):
        """
        Test returning None when no valid compatibility dates are present.

        :return:
        :rtype:
        """

        with (
            patch("esistatus.tasks.cache_handler._get_cache", return_value=None),
            patch("esistatus.tasks.requests.get") as mock_get,
        ):
            mock_response = Mock()
            mock_response.json.return_value = {
                "compatibility_dates": ["", "not-a-date"]
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = _get_latest_compatibility_date()
            self.assertIsNone(result)

    def test_handles_request_exception_and_logs_error(self):
        """
        Test handling a RequestException and logging the error.

        :return:
        :rtype:
        """

        with (
            patch("esistatus.tasks.cache_handler._get_cache", return_value=None),
            patch(
                "esistatus.tasks.requests.get",
                side_effect=requests.exceptions.RequestException("Request failed"),
            ),
            patch("esistatus.tasks.logger.debug") as mock_logger,
        ):
            result = _get_latest_compatibility_date()

            self.assertIsNone(result)
            mock_logger.assert_called_with(
                msg="Unable to get ESI compatibility dates. Error: Request failed"
            )

    def test_handles_json_decode_error_and_logs_message(self):
        """
        Test handling a JSONDecodeError and logging the message.

        :return:
        :rtype:
        """

        with (
            patch("esistatus.tasks.cache_handler._get_cache", return_value=None),
            patch("esistatus.tasks.requests.get") as mock_get,
            patch("esistatus.tasks.logger.debug") as mock_logger,
        ):
            mock_response = Mock()
            mock_response.json.side_effect = json.JSONDecodeError(
                "Expecting value", "", 0
            )
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = _get_latest_compatibility_date()

            self.assertIsNone(result)
            mock_logger.assert_called_with(
                msg="Unable to get ESI status. ESI returning gibberish, I can't understand …"
            )


class TestHelperGetESIStatusJson(BaseTestCase):
    """
    Test the _get_esi_status_json function.
    """

    def test_retrieves_esi_status_successfully(self):
        """
        Test retrieving the ESI status successfully.

        :return:
        :rtype:
        """

        with (
            patch("esistatus.tasks.requests.get") as mock_get,
            patch("esistatus.tasks.logger.info") as mock_logger,
        ):
            mock_response = Mock()
            mock_response.json.return_value = {"status": "ok"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = _get_esi_status_json("2023-10-01")

            self.assertEqual(result, {"status": "ok"})
            mock_logger.assert_called_once_with(
                "ESI status fetched successfully for for compatibility date: 2023-10-01."
            )

    def test_handles_request_exception_and_logs_error(self):
        """
        Test handling a RequestException and logging the error.

        :return:
        :rtype:
        """

        with (
            patch(
                "esistatus.tasks.requests.get",
                side_effect=requests.exceptions.RequestException("Request failed"),
            ),
            patch("esistatus.tasks.logger.error") as mock_logger,
        ):
            result = _get_esi_status_json("2023-10-01")

            self.assertIsNone(result)
            mock_logger.assert_called_once_with(
                "Unable to update ESI status. Error: Request failed"
            )

    def test_handles_json_decode_error_and_logs_message(self):
        """
        Test handling a JSONDecodeError and logging the message.

        :return:
        :rtype:
        """

        with (
            patch("esistatus.tasks.requests.get") as mock_get,
            patch("esistatus.tasks.logger.error") as mock_logger,
        ):
            mock_response = Mock()
            mock_response.json.side_effect = json.JSONDecodeError(
                "Expecting value", "", 0
            )
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = _get_esi_status_json("2023-10-01")

            self.assertIsNone(result)
            mock_logger.assert_called_once_with(
                "Unable to update ESI status. ESI returned invalid JSON."
            )


class TestHelperGetOpenAPISpecsJson(BaseTestCase):
    """
    Test the _get_openapi_specs_json function.
    """

    def test_fetches_openapi_specs_successfully(self):
        """
        Test fetching the OpenAPI specs successfully.

        :return:
        :rtype:
        """

        with (
            patch("esistatus.tasks.cache_handler._get_cache", return_value=None),
            patch("esistatus.tasks.requests.get") as mock_get,
            patch("esistatus.tasks.cache_handler._set_cache") as mock_set_cache,
            patch("esistatus.tasks.logger.info") as mock_logger,
        ):
            mock_response = Mock()
            mock_response.json.return_value = {"openapi": "3.0.0"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = _get_openapi_specs_json("2023-10-01")

            self.assertEqual(result, {"openapi": "3.0.0"})
            mock_logger.assert_called_once_with(
                "ESI OpenAPI specs fetched successfully for compatibility date: 2023-10-01."
            )
            mock_set_cache.assert_called_once_with(
                "https://esi.evetech.net/meta/openapi.json?compatibility_date=2023-10-01",
                {"openapi": "3.0.0"},
            )

    def test_uses_cached_openapi_specs_if_available(self):
        """
        Test using cached OpenAPI specs if available.

        :return:
        :rtype:
        """

        with (
            patch(
                "esistatus.tasks.cache_handler._get_cache",
                return_value={"openapi": "3.0.0"},
            ),
            patch("esistatus.tasks.logger.debug") as mock_logger,
        ):
            result = _get_openapi_specs_json("2023-10-01")

            self.assertEqual(result, {"openapi": "3.0.0"})
            mock_logger.assert_called_once_with(
                msg="Using cached ESI OpenAPI specs for compatibility date: 2023-10-01."
            )

    def test_handles_request_exception_and_logs_error(self):
        """
        Test handling a RequestException and logging the error.

        :return:
        :rtype:
        """

        with (
            patch("esistatus.tasks.cache_handler._get_cache", return_value=None),
            patch(
                "esistatus.tasks.requests.get",
                side_effect=requests.exceptions.RequestException("Request failed"),
            ),
            patch("esistatus.tasks.logger.error") as mock_logger,
        ):
            result = _get_openapi_specs_json("2023-10-01")

            self.assertIsNone(result)
            mock_logger.assert_called_once_with(
                "Unable to fetch ESI OpenAPI specs. Error: Request failed"
            )

    def test_handles_json_decode_error_and_logs_message(self):
        """
        Test handling a JSONDecodeError and logging the message.

        :return:
        :rtype:
        """

        with (
            patch("esistatus.tasks.cache_handler._get_cache", return_value=None),
            patch("esistatus.tasks.requests.get") as mock_get,
            patch("esistatus.tasks.logger.error") as mock_logger,
        ):
            mock_response = Mock()
            mock_response.json.side_effect = json.JSONDecodeError(
                "Expecting value", "", 0
            )
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = _get_openapi_specs_json("2023-10-01")
            self.assertIsNone(result)
            mock_logger.assert_called_once_with(
                "Unable to fetch ESI OpenAPI specs. ESI returned invalid JSON."
            )


class TestUpdateESIStatus(BaseTestCase):
    """
    Test the update_esi_status task.
    """

    def test_updates_esi_status_successfully(self):
        """
        Test updating the ESI status successfully.

        :return:
        :rtype:
        """

        with (
            patch(
                "esistatus.tasks._get_latest_compatibility_date",
                return_value="2023-10-01",
            ) as mock_latest,
            patch(
                "esistatus.tasks._get_esi_status_json", return_value={"status": "ok"}
            ) as mock_status,
            patch(
                "esistatus.tasks._get_openapi_specs_json",
                return_value={"openapi": "3.0.0"},
            ) as mock_specs,
            patch("esistatus.tasks.logger.debug") as mock_debug,
        ):
            update_esi_status()

            mock_debug.assert_any_call("Starting ESI status update task.")
            mock_latest.assert_called_once()
            mock_status.assert_called_once_with(compatibility_date="2023-10-01")
            mock_specs.assert_called_once_with(compatibility_date="2023-10-01")

    def test_logs_error_when_compatibility_date_is_none(self):
        with (
            patch("esistatus.tasks._get_latest_compatibility_date", return_value=None),
            patch("esistatus.tasks.logger.error") as mock_error,
        ):
            update_esi_status()
            mock_error.assert_called_once_with(
                "Failed to retrieve latest compatibility date."
            )

    def logs_error_when_esi_status_is_none(self):
        """
        Test logging an error when ESI status is None.

        :return:
        :rtype:
        """

        with (
            patch(
                "esistatus.tasks._get_latest_compatibility_date",
                return_value="2023-10-01",
            ),
            patch("esistatus.tasks._get_esi_status_json", return_value=None),
            patch(
                "esistatus.tasks._get_openapi_specs_json",
                return_value={"openapi": "3.0.0"},
            ),
            patch("esistatus.tasks.logger.error") as mock_error,
        ):
            update_esi_status()

            mock_error.assert_called_once_with(
                "Failed to retrieve ESI status or OpenAPI specs."
            )

    def test_logs_error_when_openapi_specs_is_none(self):
        """
        Test logging an error when OpenAPI specs is None.

        :return:
        :rtype:
        """

        with (
            patch(
                "esistatus.tasks._get_latest_compatibility_date",
                return_value="2023-10-01",
            ),
            patch(
                "esistatus.tasks._get_esi_status_json", return_value={"status": "ok"}
            ),
            patch("esistatus.tasks._get_openapi_specs_json", return_value=None),
            patch("esistatus.tasks.logger.error") as mock_error,
        ):
            update_esi_status()

            mock_error.assert_called_once_with(
                "Failed to retrieve ESI status or OpenAPI specs."
            )
