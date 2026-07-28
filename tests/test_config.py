import os
from unittest.mock import patch

from backend.core.config import Settings


def test_settings_can_be_instantiated():
    """Verify Settings can be instantiated with a mocked DEEPSEEK_API_KEY.

    We use clear=True to isolate from the user's .env file, and provide a
    dummy value for all required fields.
    """
    with patch.dict(
        os.environ,
        {
            "DEEPSEEK_API_KEY": "test-key",
            "LANGCHAIN_TRACING_V2": "",
            "LANGCHAIN_API_KEY": "",
            "LANGCHAIN_PROJECT": "",
        },
        clear=True,
    ):
        settings = Settings()
        assert settings.DEEPSEEK_API_KEY == "test-key"
        assert settings.LANGCHAIN_TRACING_V2 == ""
        assert settings.LANGCHAIN_API_KEY == ""
        assert settings.LANGCHAIN_PROJECT == ""