"""Configuration default and validation tests."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_load_safe_development_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "CareerPilot AI"
    assert settings.database_url == "sqlite:///./careerpilot.db"
    assert settings.openai_api_key is None
    assert settings.max_agent_retries == 2
    assert settings.max_upload_size_mb == 5


def test_settings_reject_invalid_numeric_values() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, api_port=0, max_upload_size_mb=0)
