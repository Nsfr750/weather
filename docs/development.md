# Development Guide

Welcome to the Weather App development guide. This document provides information for developers who want to contribute to the project.

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- pip (Python package manager)
- Virtual environment (recommended)

### Setting Up the Development Environment

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/your-username/weather.git
   cd weather
   ```

2. Create and activate a virtual environment:

   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Unix/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

4. Install the package in development mode:

   ```bash
   pip install -e .
   ```

## Project Structure

```text
weather/
├── script/               # Main application code
│   ├── providers/        # Weather provider implementations
│   ├── translations.py   # Translation strings
│   ├── main.py           # Main application entry point
│   └── ...
├── tests/                # Test files
├── docs/                 # Documentation
└── requirements*.txt     # Dependencies
```

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use type hints for all function signatures
- Document all public functions and classes with docstrings
- Keep lines under 88 characters (Black's default)

### Formatting

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking

Run the formatters and linters:

```bash
black .
isort .
flake8
mypy .
```

## Testing

### Running Tests

```bash
pytest
```

### Writing Tests

- Place test files in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names starting with `test_`
- Mock external API calls

Example test:

```python
def test_temperature_conversion():
    assert convert_f_to_c(32) == 0
    assert convert_f_to_c(212) == 100
```

## Adding a New Feature

1. Create a new branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style

3. Add tests for your changes

4. Update documentation if needed

5. Run tests and linters:

   ```bash
   pytest
   black .
   isort .
   flake8
   mypy .
   ```

6. Commit your changes with a descriptive message:

   ```bash
   git commit -m "Add feature: your feature description"
   ```

7. Push to your fork and create a pull request

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for added functionality in a backward-compatible manner
- **PATCH** version for backward-compatible bug fixes

Update the version in `script/version.py` when making a new release.

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request with a clear description of the changes
6. Reference any related issues
7. Ensure all tests pass
8. Get your code reviewed

## Code Review Guidelines

- Be constructive and respectful
- Focus on the code, not the person
- Explain the reason for requested changes
- Keep feedback specific and actionable
- Acknowledge good practices

## Issue Tracking

We use GitHub Issues to track bugs and feature requests. Before creating a new issue, please check if a similar issue already exists.

### Bug Reports

When reporting a bug, please include:

1. Steps to reproduce the issue
2. Expected behavior
3. Actual behavior
4. Environment details (OS, Python version, etc.)
5. Error messages or logs

### Feature Requests

For feature requests, please include:

1. Description of the feature
2. Use cases
3. Proposed implementation (if any)

## Documentation

- Keep documentation up-to-date with code changes
- Update README.md for significant changes
- Add docstrings to all public functions and classes
- Document any new configuration options

## License

By contributing to this project, you agree that your contributions will be licensed under the [GPLv3 License](LICENSE).
