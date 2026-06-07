"""`python -m vaos` entrypoint config validation (#20/W3). The serve loop itself is
thin I/O (smoke-tested with a token); this pins the fail-fast checks. Fields are set
explicitly so the test is independent of any local .env."""

from vaos.__main__ import _missing_config
from vaos.config import Settings


def _settings(**overrides: object) -> Settings:
    base: dict[str, object] = {
        "telegram_bot_token": "", "telegram_allowlist": "",
        "llm_provider": "anthropic", "anthropic_api_key": "", "azure_openai_api_key": "",
    }
    return Settings(**{**base, **overrides})  # type: ignore[arg-type]


def test_missing_config_lists_absent_required_vars() -> None:
    missing = _missing_config(_settings())
    assert "TELEGRAM_BOT_TOKEN" in missing
    assert "TELEGRAM_ALLOWLIST" in missing
    assert "ANTHROPIC_API_KEY" in missing


def test_missing_config_empty_when_all_present() -> None:
    assert _missing_config(_settings(
        telegram_bot_token="t", telegram_allowlist="8", anthropic_api_key="k"
    )) == []


def test_azure_provider_checks_azure_key_not_anthropic() -> None:
    missing = _missing_config(_settings(
        telegram_bot_token="t", telegram_allowlist="8", llm_provider="azure_openai"
    ))
    assert "AZURE_OPENAI_API_KEY" in missing
    assert "ANTHROPIC_API_KEY" not in missing
