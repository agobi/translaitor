# Contributing to PPTX Slide Translator

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/slidetranslator.git
   cd slidetranslator
   ```

2. **Set up development environment:**
   ```bash
   ./setup.sh
   pip install -r requirements-dev.txt
   ```

3. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Quality Standards

### Linting with Ruff

All code must pass Ruff linting checks:

```bash
# Check for issues
make lint

# Auto-fix issues
ruff check --fix .

# Format code
make format
```

### Type Checking with Mypy

All code should pass mypy type checking:

```bash
make type-check
```

### Run All Checks

Before committing, run all checks:

```bash
make check
```

## Continuous Integration

All pull requests are automatically checked with GitHub Actions:
- **Ruff Linting**: Code must pass all linting rules
- **Ruff Formatting**: Code must be properly formatted
- **Mypy Type Checking**: Code must pass type checking

You can see the CI status on your pull request. If checks fail, review the logs and fix the issues locally before pushing again.

## Pull Request Process

1. **Update your fork:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Make your changes:**
   - Write clean, documented code
   - Follow existing code style
   - Add type hints where appropriate

3. **Test locally:**
   ```bash
   make check
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request:**
   - Provide a clear description of your changes
   - Reference any related issues
   - Wait for CI checks to pass

## Code Style Guidelines

- **Line length**: Max 100 characters
- **Imports**: Sorted with isort (handled by Ruff)
- **Formatting**: Follow Ruff formatter style (similar to Black)
- **Type hints**: Use type hints for function parameters and returns where possible
- **Docstrings**: Use Google-style docstrings for functions and classes

### Example Function

```python
def extract_text_from_pptx(pptx_path: str) -> dict:
    """Extract all text from a PPTX file in deterministic order.
    
    Args:
        pptx_path: Path to the PPTX file
        
    Returns:
        dict: JSON structure with slides and texts
    """
    # Implementation here
    pass
```

## Testing

When adding new features:
- Test manually with sample PPTX files
- Verify formatting preservation
- Test error handling

Future: We plan to add automated tests with pytest.

## Documentation

When adding features:
- Update README.md with new usage examples
- Update QUICKSTART.md if it affects basic usage
- Update CONFIGURATION.md for new configuration options
- Add docstrings to all functions

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about contributing
- Documentation improvements

## License

By contributing, you agree that your contributions will be licensed under the BSD 3-Clause License.
