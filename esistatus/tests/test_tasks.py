# Standard Library
import json
from unittest import mock
from unittest.mock import Mock, patch

# Third Party
import requests

# AA ESI Status
from esistatus.tasks import (
    _enrich_status_json,
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

    def test_retrieves_cached_compatibility_date(self):
        """
        Test retrieving the cached compatibility date.

        :return:
        :rtype:
        """

        with mock.patch(
            "esistatus.handler.cache.Cache.get", return_value=self.latest_date
        ) as mock_cache:
            result = _get_latest_compatibility_date()

            self.assertEqual(result, self.latest_date)
            mock_cache.assert_called_once()

    def test_retrieves_latest_compatibility_date_from_api(self):
        """
        Test retrieving the latest compatibility date from the API.

        :return:
        :rtype:
        """

        mock_response = mock.Mock()
        mock_response.json.return_value = self.compatibility_date_json

        with (
            mock.patch("esistatus.handler.cache.Cache.get", return_value=None),
            mock.patch(
                "esistatus.tasks.requests.get", return_value=mock_response
            ) as mock_get,
            mock.patch("esistatus.handler.cache.Cache.set") as mock_set_cache,
        ):
            result = _get_latest_compatibility_date()

            self.assertEqual(result, self.latest_date)
            mock_get.assert_called_once()
            mock_set_cache.assert_called_once_with(value=self.latest_date)

    def test_skips_invalid_dates_in_api_response(self):
        """
        Test skipping invalid dates in the API response.

        :return:
        :rtype:
        """

        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "compatibility_dates": ["invalid-date", "2023-10-01"]
        }

        with (
            mock.patch("esistatus.handler.cache.Cache.get", return_value=None),
            mock.patch("esistatus.handler.cache.Cache.set") as mock_set_cache,
            mock.patch("esistatus.tasks.requests.get", return_value=mock_response),
        ):
            result = _get_latest_compatibility_date()

            self.assertEqual(result, "2023-10-01")
            mock_set_cache.assert_called_once_with(value="2023-10-01")

    def test_returns_none_when_no_valid_dates_found(self):
        """
        Test returning None when no valid dates are found.

        :return:
        :rtype:
        """

        mock_response = mock.Mock()
        mock_response.json.return_value = {"compatibility_dates": ["invalid-date"]}

        with (
            mock.patch("esistatus.handler.cache.Cache.get", return_value=None),
            mock.patch("esistatus.tasks.requests.get", return_value=mock_response),
        ):
            result = _get_latest_compatibility_date()

            self.assertIsNone(result)

    def test_handles_request_exception(self):
        """
        Test handling a RequestException.

        :return:
        :rtype:
        """

        with (
            mock.patch("esistatus.handler.cache.Cache.get", return_value=None),
            mock.patch(
                "esistatus.tasks.requests.get",
                side_effect=requests.exceptions.RequestException,
            ),
        ):
            result = _get_latest_compatibility_date()

            self.assertIsNone(result)

    def test_skips_non_string_dates(self):
        """
        Test skipping non-string dates in the API response.

        :return:
        :rtype:
        """

        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "compatibility_dates": [123, None, "2023-10-01"]
        }

        with (
            mock.patch("esistatus.handler.cache.Cache.get", return_value=None),
            mock.patch("esistatus.handler.cache.Cache.set") as mock_set_cache,
            mock.patch("esistatus.tasks.requests.get", return_value=mock_response),
        ):
            result = _get_latest_compatibility_date()

            self.assertEqual(result, "2023-10-01")
            mock_set_cache.assert_called_once_with(value="2023-10-01")

    def test_handles_empty_dates_list(self):
        """
        Test handling an empty dates list.

        :return:
        :rtype:
        """

        mock_response = mock.Mock()
        mock_response.json.return_value = {"compatibility_dates": []}

        with (
            mock.patch("esistatus.handler.cache.Cache.get", return_value=None),
            mock.patch("esistatus.tasks.requests.get", return_value=mock_response),
        ):
            result = _get_latest_compatibility_date()

            self.assertIsNone(result)

    def test_handles_invalid_json_response(self):
        """
        Test handling an invalid JSON response.

        :return:
        :rtype:
        """

        mock_response = mock.Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)

        with (
            mock.patch("esistatus.handler.cache.Cache.get", return_value=None),
            mock.patch("esistatus.tasks.requests.get", return_value=mock_response),
        ):
            result = _get_latest_compatibility_date()

            self.assertIsNone(result)


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
            patch("esistatus.handler.cache.Cache.get", return_value=None),
            patch("esistatus.tasks.requests.get") as mock_get,
            patch("esistatus.handler.cache.Cache.set") as mock_set_cache,
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
            mock_set_cache.assert_called_once_with(value={"openapi": "3.0.0"})

    def test_uses_cached_openapi_specs_if_available(self):
        """
        Test using cached OpenAPI specs if available.

        :return:
        :rtype:
        """

        with (
            patch(
                "esistatus.handler.cache.Cache.get", return_value={"openapi": "3.0.0"}
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
            patch("esistatus.handler.cache.Cache.get", return_value=None),
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
            patch("esistatus.handler.cache.Cache.get", return_value=None),
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


class TestHelperAddTagsToStatus(BaseTestCase):
    """
    Test the _enrich_status_json function.
    """

    def test_adds_tags_to_routes_with_matching_openapi_specs(self):
        """
        Test adding tags to routes with matching OpenAPI specs.

        :return:
        :rtype:
        """

        status = {"routes": [{"path": "/path1", "method": "GET"}]}
        openapi = {"paths": {"/path1": {"get": {"tags": ["Public"]}}}}

        result = _enrich_status_json(status, openapi)

        self.assertEqual(result[0]["tags"], ["Public"])

    def test_assigns_deprecated_tag_when_no_matching_openapi_specs(self):
        """
        Test assigning the "Deprecated" tag when there are no matching OpenAPI specs.

        :return:
        :rtype:
        """

        status = {"routes": [{"path": "/path1", "method": "GET"}]}
        openapi = {"paths": {}}

        result = _enrich_status_json(status, openapi)

        self.assertEqual(result[0]["tags"], ["Deprecated"])

    def test_handles_multiple_routes_with_different_tags(self):
        """
        Test handling multiple routes with different tags.

        :return:
        :rtype:
        """

        status = {
            "routes": [
                {"path": "/path1", "method": "GET"},
                {"path": "/path2", "method": "POST"},
            ]
        }
        openapi = {
            "paths": {
                "/path1": {"get": {"tags": ["Public"]}},
                "/path2": {"post": {"tags": ["Private"]}},
            }
        }

        result = _enrich_status_json(status, openapi)

        self.assertEqual(result[0]["tags"], ["Public"])
        self.assertEqual(result[1]["tags"], ["Private"])

    def test_handles_empty_routes_list(self):
        """
        Test handling an empty routes list.

        :return:
        :rtype:
        """

        status = {"routes": []}
        openapi = {"paths": {"/path1": {"get": {"tags": ["Public"]}}}}

        result = _enrich_status_json(status, openapi)

        self.assertEqual(result, [])

    def test_assigns_deprecated_tag_when_method_is_missing_in_openapi(self):
        """
        Test assigning the "Deprecated" tag when the method is missing in OpenAPI specs.

        :return:
        :rtype:
        """

        status = {"routes": [{"path": "/path1", "method": "GET"}]}
        openapi = {"paths": {"/path1": {}}}

        result = _enrich_status_json(status, openapi)

        self.assertEqual(result[0]["tags"], ["Deprecated"])


class TestUpdateESIStatus(BaseTestCase):
    """
    Test the update_esi_status task.
    """

    def test_updates_status_in_database_when_all_data_is_valid(self):
        """
        Test updating the status in the database when all data is valid.

        :return:
        :rtype:
        """

        with (
            mock.patch(
                "esistatus.tasks._get_latest_compatibility_date",
                return_value="2023-10-01",
            ),
            mock.patch(
                "esistatus.tasks._get_esi_status_json",
                return_value={"routes": [{"method": "GET", "path": "/alliances"}]},
            ),
            mock.patch(
                "esistatus.tasks._get_openapi_specs_json",
                return_value={
                    "paths": {"/alliances": {"get": {"tags": ["alliances"]}}}
                },
            ),
            mock.patch(
                "esistatus.tasks.EsiStatus.objects.update_or_create"
            ) as mock_update,
        ):
            update_esi_status()

            mock_update.assert_called_once_with(
                pk=1,
                defaults={
                    "compatibility_date": "2023-10-01",
                    "status_data": [
                        {
                            "method": "GET",
                            "path": "/alliances",
                            "description": None,
                            "operation_id": None,
                            "summary": None,
                            "tags": ["alliances"],
                        }
                    ],
                },
            )

    def test_skips_status_update_when_compatibility_date_is_none(self):
        """
        Test skipping the status update when the compatibility date is None.

        :return:
        :rtype:
        """

        with (
            mock.patch(
                "esistatus.tasks._get_latest_compatibility_date", return_value=None
            ),
            mock.patch("esistatus.tasks.logger.error") as mock_logger,
        ):
            update_esi_status()

            mock_logger.assert_called_with(
                "Failed to retrieve latest compatibility date."
            )

    def test_logs_error_when_esi_status_is_none(self):
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

    def test_skips_database_update_when_no_tags_in_enriched_status(self):
        enriched_status = [{"path": "/path1", "method": "GET", "tags": []}]
        with (
            mock.patch(
                "esistatus.tasks._get_latest_compatibility_date",
                return_value="2023-10-01",
            ),
            mock.patch(
                "esistatus.tasks._get_esi_status_json",
                return_value={"routes": [{"path": "/path1", "method": "GET"}]},
            ),
            mock.patch(
                "esistatus.tasks._get_openapi_specs_json",
                return_value={"paths": {}},
            ),
            mock.patch(
                "esistatus.tasks._enrich_status_json", return_value=enriched_status
            ),
            mock.patch("esistatus.tasks.logger.debug") as mock_debug,
            mock.patch(
                "esistatus.tasks.EsiStatus.objects.update_or_create"
            ) as mock_update,
        ):
            update_esi_status()
            mock_debug.assert_any_call(
                "Enriched ESI status has no tags. Skipping database update."
            )
            mock_update.assert_not_called()
