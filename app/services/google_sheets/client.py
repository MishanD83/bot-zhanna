import json
from datetime import datetime
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource


SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
)


class GoogleSheetsClient:
    """Клиент для записи данных клиентов в Google Sheets."""

    def __init__(
        self,
        credentials_file: Path | None,
        spreadsheet_id: str,
        credentials_json: str | None = None,
    ) -> None:
        self._credentials_file = credentials_file
        self._credentials_json = credentials_json
        self._spreadsheet_id = spreadsheet_id
        self._service: Resource | None = None

    @property
    def service(self) -> Resource:
        """Ленивая инициализация Google Sheets API."""

        if self._service is None:
            if self._credentials_json:
                try:
                    service_account_info = json.loads(self._credentials_json)
                except (json.JSONDecodeError, TypeError):
                    raise ValueError(
                        "GOOGLE_CREDENTIALS_JSON must contain valid service-account JSON."
                    ) from None

                try:
                    credentials = Credentials.from_service_account_info(
                        service_account_info,
                        scopes=SCOPES,
                    )
                except (KeyError, TypeError, ValueError):
                    raise ValueError(
                        "GOOGLE_CREDENTIALS_JSON is not a valid service-account credential."
                    ) from None
            elif self._credentials_file is not None:
                try:
                    credentials = Credentials.from_service_account_file(
                        str(self._credentials_file),
                        scopes=SCOPES,
                    )
                except FileNotFoundError:
                    raise FileNotFoundError(
                        "Google service-account file not found; configure "
                        "GOOGLE_CREDENTIALS_JSON or GOOGLE_CREDENTIALS_FILE."
                    ) from None
                except (KeyError, TypeError, ValueError):
                    raise ValueError(
                        "Google service-account file is not a valid credential."
                    ) from None
            else:
                raise ValueError(
                    "Google credentials are not configured; set "
                    "GOOGLE_CREDENTIALS_JSON or GOOGLE_CREDENTIALS_FILE."
                )

            self._service = build(
                "sheets",
                "v4",
                credentials=credentials,
            )

        return self._service

    @property
    def spreadsheet_id(self) -> str:
        return self._spreadsheet_id

    def append_client(
        self,
        name: str,
        country: str,
        interests: str,
        source: str,
        telegram_username: str,
        telegram_id: int,
    ) -> None:
        """Добавляет нового клиента в таблицу."""

        chat_link = ""

        if telegram_username:
            chat_link = (
                f"https://t.me/"
                f"{telegram_username.lstrip('@')}"
            )

        row = [
            datetime.now().strftime(
                "%d.%m.%Y %H:%M"
            ),
            "Готово",
            name,
            country,
            interests,
            source,
            telegram_username,
            str(telegram_id),
            chat_link,
        ]

        body = {
            "values": [row]
        }

        (
            self.service
            .spreadsheets()
            .values()
            .append(
                spreadsheetId=self._spreadsheet_id,
                range="A:I",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
