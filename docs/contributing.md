# Contributing

Thank you for your interest in contributing to Django SSLCOMMERZ! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/your-username/django-sslcommerz.git
cd django-sslcommerz

# Run the automated setup script
./scripts/setup-dev.sh
```

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run initial tests
python -m pytest tests.py
```

## Development Workflow

### 1. Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally
3. Add upstream remote:

```bash
git remote add upstream https://github.com/original-owner/django-sslcommerz.git
```

### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Write your code
- Add tests for new functionality
- Update documentation if needed
- Follow coding standards (enforced by pre-commit hooks)

### 4. Test Your Changes

```bash
# Run all tests
./scripts/test.sh

# Run specific test types
./scripts/test.sh unit
./scripts/test.sh integration
./scripts/test.sh quality
./scripts/test.sh security
```

### 5. Commit and Push

```bash
git add .
git commit -m "feat: add new feature description"
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to GitHub and create a pull request
2. Fill out the pull request template
3. Wait for review and address feedback

## Code Standards

### Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

These are automatically enforced by pre-commit hooks.

### Commit Messages

We follow the [Conventional Commits](https://conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: add refund processing functionality
fix: resolve IPN validation issue
docs: update configuration guide
test: add unit tests for payment client
```

### Code Review Guidelines

**For Authors:**
- Ensure all tests pass
- Write clear commit messages
- Include tests for new features
- Update documentation as needed
- Keep pull requests focused and small

**For Reviewers:**
- Be constructive and respectful
- Test the changes locally
- Check for security implications
- Verify documentation updates
- Ensure backward compatibility

## Testing

### Running Tests

```bash
# Run all tests with coverage
./scripts/test.sh

# Run specific test categories
./scripts/test.sh unit           # Unit tests only
./scripts/test.sh integration    # Integration tests
./scripts/test.sh quality        # Code quality checks
./scripts/test.sh security       # Security tests
./scripts/test.sh performance    # Performance tests
```

### Writing Tests

#### Unit Tests

```python
# tests/test_client.py
import unittest.mock as mock
from django.test import TestCase
from sslcommerz.client import SSLCommerzClient

class SSLCommerzClientTest(TestCase):
    
    def setUp(self):
        self.client = SSLCommerzClient()
    
    @mock.patch('sslcommerz.client.requests.Session.post')
    def test_payment_initiation_success(self, mock_post):
        # Mock successful response
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            'status': 'SUCCESS',
            'GatewayPageURL': 'https://sandbox.sslcommerz.com/test'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test data
        payment_data = {
            'total_amount': 100.00,
            'currency': 'BDT',
            'tran_id': 'TEST_123',
            'cus_name': 'Test User',
            'cus_email': 'test@example.com',
            'cus_phone': '01700000000'
        }
        
        # Execute test
        result = self.client.initiate_payment(payment_data)
        
        # Assertions
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertIn('GatewayPageURL', result)
        mock_post.assert_called_once()
```

#### Integration Tests

```python
# tests/test_integration.py
from django.test import TestCase, override_settings
from sslcommerz.models import Transaction

@override_settings(
    SSLCOMMERZ={
        'STORE_ID': 'test_store',
        'STORE_PASSWORD': 'test_password',
        'IS_SANDBOX': True,
    }
)
class IntegrationTest(TestCase):
    
    def test_transaction_creation_and_update(self):
        # Create transaction
        transaction = Transaction.objects.create(
            tran_id='TEST_123',
            amount=100.00,
            currency='BDT',
            customer_name='Test User',
            customer_email='test@example.com',
            customer_phone='01700000000'
        )
        
        # Test initial state
        self.assertEqual(transaction.status, 'PENDING')
        self.assertFalse(transaction.is_validated)
        
        # Test status update
        transaction.mark_as_successful()
        self.assertEqual(transaction.status, 'VALID')
        self.assertIsNotNone(transaction.payment_completed_at)
```

### Test Coverage

We aim for at least 90% test coverage. Check coverage with:

```bash
coverage run -m pytest tests.py
coverage report
coverage html  # Generate HTML report
```

## Documentation

### Building Documentation

```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme myst-parser

# Build documentation
cd docs
make html

# Serve documentation locally
python -m http.server 8080 -d _build/html
```

### Writing Documentation

- Use Markdown for most documentation
- Use reStructuredText for complex formatting
- Include code examples
- Update API documentation when adding new features
- Add docstrings to all public functions and classes

### Docstring Style

We use Google-style docstrings:

```python
def initiate_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Initiate a payment session with SSLCOMMERZ.
    
    Args:
        payment_data: Dictionary containing payment information including
            total_amount, currency, transaction ID, and customer details.
            
    Returns:
        Dictionary containing API response with status and gateway URL.
        
    Raises:
        SSLCommerzAPIError: If API request fails.
        SSLCommerzValidationError: If payment data is invalid.
        
    Example:
        >>> client = SSLCommerzClient()
        >>> payment_data = {
        ...     'total_amount': 100.00,
        ...     'currency': 'BDT',
        ...     'tran_id': 'TXN_123',
        ...     'cus_name': 'John Doe',
        ...     'cus_email': 'john@example.com',
        ...     'cus_phone': '01700000000'
        ... }
        >>> response = client.initiate_payment(payment_data)
        >>> print(response['status'])
        SUCCESS
    """
```

## Release Process

### Version Management

We use semantic versioning (MAJOR.MINOR.PATCH):

```bash
# Bump version
./scripts/version.sh patch  # 1.0.0 -> 1.0.1
./scripts/version.sh minor  # 1.0.0 -> 1.1.0
./scripts/version.sh major  # 1.0.0 -> 2.0.0
```

### Creating Releases

1. **Update Version and Changelog**
   ```bash
   ./scripts/version.sh minor
   # Update CHANGELOG.md with new features
   ```

2. **Test Release**
   ```bash
   ./scripts/deploy.sh test 1.1.0
   ```

3. **Create GitHub Release**
   - Go to GitHub Releases
   - Create new release with tag `v1.1.0`
   - GitHub Actions will automatically deploy to PyPI

### Changelog Guidelines

Follow [Keep a Changelog](https://keepachangelog.com/):

```markdown
## [1.1.0] - 2025-10-15

### Added
- New refund processing functionality
- Support for multiple store configurations

### Changed
- Improved error handling in IPN processing
- Updated documentation with more examples

### Fixed
- Fixed issue with amount validation
- Resolved timezone handling in transaction models

### Security
- Enhanced IPN validation security
```

## Issue and Bug Reporting

### Reporting Bugs

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - Django version
   - Package version
   - Operating system

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Error messages and stack traces

3. **Minimal Example**
   - Provide minimal code that reproduces the issue
   - Include relevant configuration

### Feature Requests

For feature requests:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: Suggest how it might work
3. **Alternatives**: What alternatives have you considered?
4. **Implementation**: Are you willing to implement it?

## Security

### Reporting Security Issues

**Do not open public issues for security vulnerabilities.**

Email security issues to: security@yourproject.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Never commit secrets or credentials
- Validate all input data
- Use HTTPS for all communications
- Follow Django security best practices
- Keep dependencies updated

## Community

### Communication

- **GitHub Discussions**: General questions and discussions
- **GitHub Issues**: Bug reports and feature requests
- **Email**: security@yourproject.com for security issues

### Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

Key points:
- Be respectful and inclusive
- Be collaborative
- Be constructive in feedback
- Focus on the code, not the person

## Getting Help

### Resources

- **Documentation**: Read the full documentation
- **Examples**: Check the examples directory
- **Tests**: Look at existing tests for patterns
- **Issues**: Search existing issues

### Mentorship

New contributors are welcome! If you need help:

1. Comment on the issue you want to work on
2. Ask questions in GitHub Discussions
3. Reach out to maintainers

## Recognition

Contributors are recognized in:
- CHANGELOG.md for significant contributions
- GitHub contributors page
- Release notes for major contributions

Thank you for contributing to Django SSLCOMMERZ!
