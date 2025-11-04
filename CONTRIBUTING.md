# Contributing to GLASS Data Standardizer

Thank you for your interest in contributing to GLASS Data Standardizer! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** and clone your fork
2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

4. **Run linting and formatting**:
   ```bash
   black .
   ruff check .
   isort .
   mypy .
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: description of your change"
   ```

6. **Push and create a Pull Request**

## Coding Standards

### Code Style
- Follow PEP 8 guidelines
- Use `black` for code formatting (line length: 100)
- Use `ruff` for linting
- Use `isort` for import sorting

### Type Hints
- Add type hints to all function signatures
- Use `typing` module for complex types
- Use `Optional` for nullable values

### Docstrings
- Use Google-style docstrings
- Include Args, Returns, and Raises sections where applicable
- Document complex logic inline

### Testing
- Write unit tests for new functions
- Write integration tests for workflows
- Aim for >80% code coverage
- Use descriptive test names: `test_function_name_condition`

## Commit Messages

Follow conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add support for CSV export format
fix: resolve memory leak in file merger
docs: update installation instructions
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass** locally
4. **Update CHANGELOG.md** (if exists)
5. **Request review** from maintainers

## Code Review Guidelines

- Be respectful and constructive
- Focus on code quality and maintainability
- Ask questions if something is unclear
- Suggest improvements, not just point out issues

## Running the Application Locally

```bash
# Development mode
python run.py

# Production mode
python run_production.py
```

## Questions?

- Open an issue for bugs or feature requests
- Contact the maintainers for questions

Thank you for contributing! 🎉



