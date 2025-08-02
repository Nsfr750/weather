## How to use the tests

Install pytest: ```pip install pytest```

- Test API Key Manager: ```python -m pytest tests/test_api_key_manager.py -v```
- Test Plugin Loading: ```python -m pytest tests/test_plugin_loading.py -v```
- Test Plugin System: ```python -m pytest tests/test_plugin_system.py -v```

or

- Run all tests: ```python -m pytest -v```
- Run tests with coverage: ```python -m pytest --cov=script --cov-report=html```
- Run tests with xdist: ```python -m pytest -n 4```
- Run tests with asyncio: ```python -m pytest -s```
