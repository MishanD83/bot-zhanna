from app.config.settings import Settings


def test_railway_environment_loads_google_json_as_secret(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "telegram-test-token")
    monkeypatch.setenv("ZHANNA_TELEGRAM_ID", "123456")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_JSON", '{"type":"service_account"}')
    monkeypatch.setenv("GOOGLE_SPREADSHEET_ID", "spreadsheet-id")

    config = Settings(_env_file=None)

    assert config.google_credentials_json is not None
    assert config.google_credentials_json.get_secret_value() == '{"type":"service_account"}'
    assert config.google_spreadsheet_id == "spreadsheet-id"
    assert config.google_credentials_file.name == "service_account.json"
