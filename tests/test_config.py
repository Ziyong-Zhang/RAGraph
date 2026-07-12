import os
from unittest.mock import patch

from backend.core.config import Settings


def test_settings_can_be_instantiated():
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=False):
        settings = Settings()
        assert settings.DEEPSEEK_API_KEY == "test-key"
        assert settings.LANGCHAIN_TRACING_V2 is None
        assert settings.LANGCHAIN_API_KEY is None
        assert settings.LANGCHAIN_PROJECT is None