# Contributing to Weather App

Thank you for your interest in contributing to the Weather App! We welcome all contributions, whether they're bug reports, feature requests, documentation improvements, or code contributions.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [How Can I Contribute?](#-how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Development Environment](#-development-environment)
- [Code Style Guide](#-code-style-guide)
- [Commit Message Guidelines](#-commit-message-guidelines)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Community](#-community)

## ✨ Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report any unacceptable behavior to nsfr750@yandex.com.

## 🚀 Getting Started

1. **Fork** the repository on GitHub
2. **Clone** the project to your own machine
3. **Commit** changes to your own branch
4. **Push** your work back up to your fork
5. Submit a **Pull Request** so we can review your changes

## 🤔 How Can I Contribute?

### Reporting Bugs

Bugs are tracked as [GitHub issues](https://github.com/Nsfr750/weather/issues). Create an issue with the following information:

- **Description**: A clear and concise description of the bug
- **Steps to Reproduce**: Step-by-step instructions to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Screenshots**: If applicable, add screenshots to help explain your problem
- **Environment**: OS, Python version, and any other relevant information

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/Nsfr750/weather/issues). When creating an enhancement suggestion, please include:

- A clear and descriptive title
- A detailed description of the suggested enhancement
- Why this enhancement would be useful
- Any alternative solutions or features you've considered

### Your First Code Contribution

Looking for something to work on? Check out the [TO_DO.md](TO_DO.md) file for a list of open tasks. Issues labeled as `good first issue` are a great place to start.

### Pull Requests

1. **Fork** the repository and create your branch from `main`
2. **Test** your changes thoroughly
3. **Update** the documentation if needed
4. **Ensure** your code follows the style guide
5. **Update** the CHANGELOG.md with your changes
6. **Submit** a pull request with a clear description of your changes

## 🛠 Development Environment

### Prerequisites

- Python 3.10+
- Git
- pip (Python package manager)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nsfr750/weather.git
   cd weather
   ```

2. **Set up a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Unix/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## 📝 Code Style Guide

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for static type checking

Run these tools before committing:

```bash
black .
isort .
flake8
mypy .
```

## ✏️ Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Example**:
```
feat(weather): add support for 10-day forecast

Add new API endpoint and UI components to display 10-day weather forecast.

Closes #123
```

## 🧪 Testing

We use `pytest` for testing. To run the tests:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=script --cov-report=term-missing
```

## 📖 Documentation

Documentation is stored in the `docs/` directory. When making changes to the code, please update the relevant documentation.

To build the documentation locally:

```bash
mkdocs serve
```

Then open `http://127.0.0.1:8000` in your browser.

## 🌍 Community

- **Discord**: Join our [Discord server](https://discord.gg/ryqNeuRYjD) for discussions and support
- **Issues**: Report bugs and suggest features on [GitHub Issues](https://github.com/Nsfr750/weather/issues)
- **Email**: Contact the maintainer at nsfr750@yandex.com

## 🙏 Thank You!

Your contributions to open source, large or small, make great projects like this possible. Thank you for being part of our community.
