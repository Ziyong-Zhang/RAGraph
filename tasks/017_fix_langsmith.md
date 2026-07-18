> Context: The LLM chat and graph pipeline are working, but we are not seeing any traces in LangSmith. This is a classic issue where `LANGCHAIN_*` environment variables are loaded into Pydantic settings but not explicitly synced back to the global `os.environ` early enough before the LangChain/LangSmith SDKs initialize.

> STRICT RULES:
> 1. ALL code, comments, docstrings, and commit messages MUST be strictly in English.
> 2. Ensure we use python's `os` module.

Please execute the following robust fix:

### Task 1: Force Environment Synchronization (backend/core/config.py)
In `backend/core/config.py` (or wherever your `get_settings()` function is defined):
- Import the `os` module.
- In the `get_settings()` function (or a dedicated `init_observability()` function called immediately after loading settings), explicitly sync the LangSmith variables from the loaded Pydantic settings back into `os.environ`.
- Example logic:
  
```python
  settings = Settings()
  if settings.LANGCHAIN_TRACING_V2:
      os.environ["LANGCHAIN_TRACING_V2"] = "true"
      os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY.get_secret_value()
      if settings.LANGCHAIN_PROJECT:
          os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
  

```

* Make sure this synchronization happens the very first time `get_settings()` is called.

### Task 2: Ensure Early Invocation in Entry Points

* In `backend/main.py`: Call `get_settings()` (or your sync function) at the VERY TOP of the file, immediately after standard library imports but BEFORE importing any local modules like `backend.core.chat` or any LangChain/OpenAI packages.
* In `scripts/run_integration.py`: Ensure `get_settings()` is called and the environment is synced at the very top, before the `from backend.core.workflow import ...` line.

Run `uv run pytest tests/ -v` to ensure no circular imports were introduced.
