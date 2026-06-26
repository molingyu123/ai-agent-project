import importlib


def test_settings_accepts_database_url(monkeypatch):
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://example/db")

    import config.settings as settings_module

    settings_module.get_settings.cache_clear()
    reloaded = importlib.reload(settings_module)

    assert reloaded.settings.postgres_url == "postgresql://example/db"
