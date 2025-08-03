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
  python -m pytest tests/test_enhanced_notifications.py -v
  python -m pytest tests/test_log.py -v
  python -m pytest tests/test_maps_dialog.py -v
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
- `test_enhanced_notifications.py`: Tests for the enhanced notification system
- `test_log.py`: Tests for the logging system
- `test_maps_dialog.py`: Tests for the maps dialog
- `test_menu.py`: Tests for the menu system
- `test_ui.py`: Tests for the UI system
- `test_updates.py`: Tests for the updates system
- `test_version.py`: Tests for the version system

