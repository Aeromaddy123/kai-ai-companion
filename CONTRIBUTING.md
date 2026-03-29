# Contributing to KAI

Thank you for your interest in contributing to KAI!

## Development Process

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Make your changes**
4. **Write tests** (if applicable)
5. **Commit your changes**
   ```bash
   git commit -m 'Add AmazingFeature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
7. **Open a Pull Request**

## Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write docstrings for all public functions
- Keep functions focused and small

## Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove)
- Keep the first line under 72 characters
- Reference issues when applicable

## Testing

Before submitting:
```bash
# Run tests
python -m pytest

# Check code formatting
python -m black --check .
python -m ruff check .
```

## Reporting Issues

Please include:
- Your environment (OS, Python version)
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

## Questions?

Feel free to open an issue for any questions!
