# 🤝 Contributing to AI Content Auto-Generator

Thank you for considering contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on collaboration

## How to Contribute

### Reporting Bugs

1. Check if bug already exists in Issues
2. Create new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)
   - Logs if available

### Suggesting Features

1. Open issue with `enhancement` label
2. Describe:
   - Use case
   - Proposed solution
   - Alternative approaches
   - Impact on existing features

### Pull Requests

#### Before Starting

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Check existing issues and PRs

#### Development Process

1. **Setup Development Environment**

```bash
git clone https://github.com/YOUR_USERNAME/ai-content-auto-generator.git
cd ai-content-auto-generator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dev dependencies
```

2. **Make Changes**

- Follow PEP 8 style guide
- Add docstrings to functions/classes
- Keep functions focused and small
- Update tests for new features

3. **Run Tests**

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html

# Check code style
flake8 scripts/
black scripts/ --check
```

4. **Commit Changes**

```bash
git add .
git commit -m "feat: add amazing feature"
```

**Commit Message Format:**

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(api): add support for Claude 3 Opus
fix(cache): resolve Redis connection timeout
docs(setup): add Docker installation guide
```

5. **Push Changes**

```bash
git push origin feature/amazing-feature
```

6. **Create Pull Request**

- Clear title describing change
- Reference related issues
- Describe what changed and why
- Add screenshots if UI changes
- Ensure CI passes

#### Code Style

**Python Style:**

```python
# Good
def generate_text(prompt: str, context: Optional[Dict] = None) -> str:
    """Generate text using AI.
    
    Args:
        prompt: Generation prompt
        context: Additional context
        
    Returns:
        Generated text
    """
    # Implementation
    pass

# Bad
def gen(p, c=None):
    # No docstring
    pass
```

**Async/Await:**

```python
# Use async for I/O operations
async def call_api(self, payload: Dict) -> Dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json()
```

**Error Handling:**

```python
try:
    result = await self.api_call()
except APIError as e:
    logger.error(f"API call failed: {e}")
    return await self._handle_fallback()
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise
```

## Project Structure

```
scripts/
  ├── main.py           # Main orchestrator
  ├── api_manager.py    # API management
  ├── text_generator.py # Text generation
  ├── image_generator.py # Image generation
  ├── cache_manager.py  # Caching
  ├── analytics.py      # A/B testing
  └── optimizer.py      # Optimization

tests/
  ├── test_api_manager.py
  ├── test_cache_manager.py
  └── test_content_generator.py
```

## Testing Guidelines

### Unit Tests

Test individual components:

```python
def test_api_selection(api_manager):
    api = api_manager.get_available_api('text', 'round_robin')
    assert api in api_manager.text_apis
```

### Integration Tests

Test component interactions:

```python
@pytest.mark.asyncio
async def test_full_generation_flow():
    generator = ContentGenerator()
    result = await generator.generate_text("test prompt")
    assert isinstance(result, str)
    assert len(result) > 0
```

### Mocking API Calls

```python
from unittest.mock import AsyncMock, patch

@patch('scripts.api_manager.APIManager.call_api')
async def test_with_mock(mock_call):
    mock_call.return_value = {'data': 'test result'}
    # Test code
```

## Documentation

- Update README.md for user-facing changes
- Update SETUP.md for installation changes
- Add docstrings to new functions
- Update config examples if needed

## Release Process

1. Update version in `scripts/__init__.py`
2. Update CHANGELOG.md
3. Create release tag: `git tag -a v1.1.0 -m "Release v1.1.0"`
4. Push tag: `git push origin v1.1.0`
5. Create GitHub release with notes

## Questions?

Open an issue or discussion on GitHub!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.