# Installation

## Requirements

- Python 3.8 or higher
- Django 3.2 or higher
- requests 2.25.0 or higher

## Basic Installation

Install Django SSLCOMMERZ using pip:

```bash
pip install django-sslcommerz
```

## Development Installation

For development or contributing to the project:

```bash
# Clone the repository
git clone https://github.com/your-username/django-sslcommerz.git
cd django-sslcommerz

# Install in development mode
pip install -e .[dev]
```

## Optional Dependencies

### Django REST Framework Support

If you want to use the optional REST API endpoints:

```bash
pip install django-sslcommerz[drf]
```

Or install DRF separately:

```bash
pip install djangorestframework
```

### Development Dependencies

For development, testing, and contributing:

```bash
pip install django-sslcommerz[dev]
```

This includes:
- pytest and pytest-django for testing
- black for code formatting
- flake8 for linting
- mypy for type checking
- pre-commit for git hooks

## Django Integration

Add `sslcommerz` to your Django `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    # ... your existing apps
    'sslcommerz',
    # ... other apps
]
```

## Database Migration

Run migrations to create the necessary database tables:

```bash
python manage.py migrate
```

## Verification

Test your installation:

```python
# Test import
from sslcommerz.client import SSLCommerzClient
print("Django SSLCOMMERZ installed successfully!")
```

Or use the management command:

```bash
python manage.py test_sslcommerz
```

## Next Steps

Continue to the [Quick Start Guide](quickstart.md) to begin integrating SSLCOMMERZ into your Django application.
