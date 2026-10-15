import json
import logging
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from googleapiclient.errors import HttpError

from app.services.google_sheets.client import GoogleSheetsClient


def test_service_uses_google_credentials_json() -> None:
    info = {"type": "service_account", "client_email": "bot@example.test"}
    credentials = Mock()

    with (
        patch(
            "app.services.google_sheets.client.Credentials.from_service_account_info",
            return_value=credentials,
        ) as from_info,
        patch(
            "app.services.google_sheets.client.build",
            return_value="sheets-service",
        ) as build,
    ):
        client = GoogleSheetsClient(
            credentials_file=None,
            spreadsheet_id="spreadsheet-id",
            credentials_json=json.dumps(info),
        )

        assert client.service == "sheets-service"

    from_info.assert_called_once()
    assert from_info.call_args.args[0] == info
    build.assert_called_once()


def test_service_reports_invalid_json_without_echoing_it() -> None:
    secret = "private-key-material"
    client = GoogleSheetsClient(
        credentials_file=None,
        spreadsheet_id="spreadsheet-id",
        credentials_json=secret,
    )

    with pytest.raises(ValueError, match="GOOGLE_CREDENTIALS_JSON") as error:
        _ = client.service

    assert secret not in str(error.value)


def test_service_keeps_local_credentials_file_support() -> None:
    credentials_file = Path("credentials/service_account.json")
    credentials = Mock()

    with (
        patch(
            "app.services.google_sheets.client.Credentials.from_service_account_file",
            return_value=credentials,
        ) as from_file,
        patch(
            "app.services.google_sheets.client.build",
            return_value="sheets-service",
        ),
    ):
        client = GoogleSheetsClient(
            credentials_file=credentials_file,
            spreadsheet_id="spreadsheet-id",
        )

        assert client.service == "sheets-service"

    from_file.assert_called_once_with(str(credentials_file), scopes=(
        "https://www.googleapis.com/auth/spreadsheets",
    ))


def test_append_logs_google_api_status_and_safe_traceback(caplog) -> None:
    secret = "must-not-appear-in-logs"
    response = Mock(status=403)
    error = HttpError(response, json.dumps({"error": secret}).encode())
    service = Mock()
    request = service.spreadsheets.return_value.values.return_value.append.return_value
    request.execute.side_effect = error
    client = GoogleSheetsClient(None, "spreadsheet-id", "unused")
    client._service = service

    with caplog.at_level(logging.ERROR):
        with pytest.raises(HttpError):
            client.append_client("Name", "Country", "Interest", "source", "", 123)

    assert "stage=append_request_execution" in caplog.text
    assert "exception_type=HttpError" in caplog.text
    assert "google_api_status=403" in caplog.text
    assert "Traceback (frames only)" in caplog.text
    assert secret not in caplog.text
