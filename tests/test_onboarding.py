import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.config.settings import Settings

os.environ.setdefault("BOT_TOKEN", "test-token")
os.environ.setdefault("ZHANNA_TELEGRAM_ID", "123456")

from app.handlers import onboarding


class FakeState:
    def __init__(self, data: dict) -> None:
        self.data = data

    async def get_data(self) -> dict:
        return dict(self.data)

    async def update_data(self, **values) -> None:
        self.data.update(values)


async def test_repeated_done_after_saved_does_not_append_a_second_row() -> None:
    state = FakeState(
        {
            "name": "Test",
            "country": "Testland",
            "interests": ["travel"],
            "saved_to_sheets": True,
            "notification_sent": True,
        }
    )
    message = SimpleNamespace(answer=AsyncMock())
    callback = SimpleNamespace(
        from_user=SimpleNamespace(id=42, username=None),
        message=message,
        answer=AsyncMock(),
        bot=SimpleNamespace(send_message=AsyncMock()),
    )

    with patch.object(onboarding, "GoogleSheetsClient") as client_class:
        await onboarding.process_interests_done(callback, state)
        await onboarding.process_interests_done(callback, state)

    client_class.assert_not_called()
    callback.bot.send_message.assert_not_called()
    assert message.answer.await_count == 1
    assert state.data["submission_complete"] is True


async def test_done_passes_loaded_settings_json_to_actual_client(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "test-token")
    monkeypatch.setenv("ZHANNA_TELEGRAM_ID", "123456")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_JSON", '{"type":"service_account"}')
    config = Settings(_env_file=None)
    monkeypatch.setattr(onboarding, "settings", config)
    state = FakeState(
        {"name": "Test", "country": "Testland", "interests": ["travel"]}
    )
    callback = SimpleNamespace(
        from_user=SimpleNamespace(id=42, username=None),
        message=SimpleNamespace(answer=AsyncMock()),
        answer=AsyncMock(),
        bot=SimpleNamespace(send_message=AsyncMock()),
    )

    with patch.object(onboarding, "GoogleSheetsClient") as client_class:
        client_class.return_value.append_client.side_effect = RuntimeError("stop after construction")
        await onboarding.process_interests_done(callback, state)

    client_class.assert_called_once_with(
        credentials_file=config.google_credentials_file,
        spreadsheet_id=config.google_spreadsheet_id,
        credentials_json='{"type":"service_account"}',
    )
