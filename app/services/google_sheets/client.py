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
        credentials_file: Path,
        spreadsheet_id: str,
    ) -> None:
        self._credentials_file = credentials_file
        self._spreadsheet_id = spreadsheet_id
        self._service: Resource | None = None

    @property
    def service(self) -> Resource:
        """Ленивая инициализация Google Sheets API."""

        if self._service is None:
            credentials = (
                Credentials.from_service_account_file(
                    str(self._credentials_file),
                    scopes=SCOPES,
                )
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
            "Новый контакт",
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