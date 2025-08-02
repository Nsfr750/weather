## How to use the tests

Install pytest: 
```bash
pip install pytest
```

### Running Tests

- **Run all tests**:
  ```bash
  python -m pytest -v
  ```

- **Run specific test files**:
  ```bash
  python -m pytest tests/test_api_key_manager.py -v
  python -m pytest tests/test_log.py -v
  ```

- **Run tests with coverage**:
  ```bash
  python -m pytest --cov=script --cov-report=html
  ```

- **Run tests in parallel**:
  ```bash
  python -m pytest -n 4
  ```

- **Run tests with asyncio debug output**:
  ```bash
  python -m pytest -s
  ```

### Test Organization

- `test_api_key_manager.py`: Tests for the API key management system
- `test_log.py`: Tests for the logging system
