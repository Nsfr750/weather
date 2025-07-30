# Development Guide

Welcome to the Weather App development guide. This document provides information for developers who want to contribute to the project.

## Table of Contents
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Version Control](#version-control)
- [Debugging](#debugging)
- [Performance](#performance)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- pip (Python package manager)
- Virtual environment (recommended)
- Node.js 16+ (for frontend development)
- PostgreSQL 13+ (for database development)

### Setting Up the Development Environment

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/Nsfr750/weather.git
   cd weather
   ```

2. **Set up Python virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Unix/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Set up environment variables**:
   ```bash
   # Windows
   copy .env.example .env
   
   # Unix/macOS
   cp .env.example .env
   ```
   Then edit `.env` with your configuration.

## Project Structure

```
weather/
├── script/               # Main application code
│   ├── api/             # API endpoints
│   ├── core/            # Core functionality
│   ├── models/          # Database models
│   ├── providers/       # Weather provider implementations
│   ├── static/          # Static files (CSS, JS, images)
│   ├── templates/       # HTML templates
│   ├── tests/           # Test files
│   ├── utils/           # Utility functions
│   ├── __init__.py
│   ├── config.py        # Configuration settings
│   ├── extensions.py    # Flask extensions
│   └── main.py          # Application entry point
├── migrations/          # Database migrations
├── tests/               # Integration and end-to-end tests
├── .env.example         # Example environment variables
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── MANIFEST.in
├── README.md
├── requirements-dev.txt # Development dependencies
└── setup.py
```

## Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some additional guidelines:

### Formatting

- **Line Length**: 88 characters (Black's default)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings that will be shown to users, single quotes otherwise
- **Imports**: Sorted and grouped (handled automatically by isort)

### Tools

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking
- **pre-commit**: Git hooks

Run all formatters and linters:

```bash
pre-commit run --all-files
```

Or individually:

```bash
black .
isort .
flake8
mypy .
```

### Type Hints

- Use type hints for all function signatures
- Use `Optional[T]` instead of `Union[T, None]`
- Use `List`, `Dict`, `Set`, `Tuple` from `typing` module
- Use Python 3.10+ type union syntax: `str | None`

### Docstrings

Follow Google style docstrings:

```python
def get_weather(location: str, days: int = 5) -> dict:
    """Get weather forecast for a location.

    Args:
        location: City name or coordinates (lat,lon)
        days: Number of days to forecast (1-10)

    Returns:
        Dictionary containing weather data

    Raises:
        ValueError: If location is invalid
        APIError: If weather data cannot be fetched
    """
    # Implementation
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_weather.py

# Run tests with coverage
pytest --cov=script tests/

# Run tests in parallel
pytest -n auto
```

### Writing Tests

- Place test files in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names starting with `test_`
- Group related tests in classes
- Use fixtures for common test data

Example test:

```python
import pytest
from script.weather import get_weather

class TestWeather:
    @pytest.fixture
    def sample_weather_data(self):
        return {"temperature": 25, "condition": "Sunny"}

    def test_get_weather_success(self, mocker, sample_weather_data):
        # Mock the API call
        mocker.patch("script.weather._call_weather_api", 
                    return_value=sample_weather_data)
        
        result = get_weather("London")
        assert result["temperature"] == 25
        assert result["condition"] == "Sunny"

    def test_get_weather_invalid_location(self):
        with pytest.raises(ValueError, match="Invalid location"):
            get_weather("")
```

### Test Coverage

We aim for at least 80% test coverage. Generate a coverage report:

```bash
pytest --cov=script --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

## Documentation

### Code Documentation

- Document all public APIs with docstrings
- Use type hints for better IDE support
- Keep comments focused on "why" not "what"

### API Documentation

We use Swagger/OpenAPI for API documentation. After starting the development server:

1. Visit `/docs` for interactive API documentation
2. Update `openapi.yaml` when adding new endpoints

## Version Control

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `release/*`: Release preparation

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvements
- `test`: Adding or modifying tests
- `chore`: Changes to the build process or auxiliary tools

Example:
```
feat(weather): add 10-day forecast support

Add support for fetching 10-day weather forecast from OpenWeatherMap API.

Closes #123
```

## Debugging

### VS Code

1. Set breakpoints in your code
2. Press F5 to start debugging
3. Use the debug console to inspect variables

### Command Line

```bash
# Start the development server with debugger
python -m script.main --debug

# Or use the built-in debugger
python -m pdb -m script.main
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    try:
        # Code that might fail
        logger.debug("Debug information")
        logger.info("Information message")
        logger.warning("Warning message")
    except Exception as e:
        logger.error("Error occurred", exc_info=True)
        raise
```

## Performance

### Profiling

```bash
# Run with cProfile
python -m cProfile -o profile.cprof -m script.main

# Analyze with snakeviz
snakeviz profile.cprof
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory_profiler

# Profile memory usage
mprof run python script.py
mprof plot
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a pull request

### Pull Request Guidelines

- Keep PRs small and focused
- Include tests for new features
- Update documentation as needed
- Ensure all tests pass
- Follow the code style

## Troubleshooting

### Common Issues

- **Dependency conflicts**: Try `pip install --upgrade -r requirements-dev.txt`
- **Database issues**: Run `flask db upgrade`
- **Cache problems**: Clear the cache directory or restart the application

### Getting Help

1. Check the [issues](https://github.com/Nsfr750/weather/issues)
2. Search the documentation
3. Ask for help on [Discord](https://discord.gg/ryqNeuRYjD)

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
