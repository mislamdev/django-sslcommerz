# Django SSLCOMMERZ - Complete Package Documentation

## Project Structure

```
django-sslcommerz/
├── sslcommerz/                     # Main package directory
│   ├── __init__.py                 # Package initialization
│   ├── apps.py                     # Django app configuration
│   ├── config.py                   # Configuration management
│   ├── client.py                   # SSLCOMMERZ API client
│   ├── exceptions.py               # Custom exceptions
│   ├── handlers.py                 # IPN handling
│   ├── signals.py                  # Django signals
│   ├── models.py                   # Database models
│   ├── admin.py                    # Django admin integration
│   ├── views.py                    # Django views
│   ├── drf.py                      # Django REST Framework integration
│   ├── urls.py                     # URL patterns
│   ├── utils.py                    # Utility functions
│   ├── migrations/                 # Database migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── management/                 # Management commands
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           └── test_sslcommerz.py
├── setup.py                       # Package setup
├── README.md                       # Main documentation
├── LICENSE                         # MIT License
├── MANIFEST.in                     # Package manifest
├── requirements.txt                # Core requirements
├── .env.example                    # Environment variables example
├── example_settings.py             # Django settings example
├── example_urls.py                 # URL configuration example
├── examples.py                     # Comprehensive usage examples
└── tests.py                       # Test suite
```

## Core Features Implemented

### 1. **Production-Ready Architecture**
- Robust error handling with custom exceptions
- Comprehensive logging support
- Configuration validation
- Thread-safe client implementation
- Proper Django app integration

### 2. **Flexible Configuration System**
- Django settings integration
- Environment variables support (.env)
- Multiple store support
- Sandbox/production mode switching
- Configurable timeouts and SSL verification

### 3. **Complete API Coverage**
- ✅ Payment initiation
- ✅ IPN (Instant Payment Notification) handling
- ✅ Transaction validation
- ✅ Refund processing
- ✅ Sandbox and live environment support

### 4. **Django Integration**
- Models for transaction tracking
- Django admin interface
- Management commands
- Database migrations
- Signal system for extensibility

### 5. **Optional DRF Support**
- REST API endpoints
- Serializers for data validation
- ViewSets for CRUD operations
- No import errors when DRF is absent

### 6. **Developer Experience**
- Comprehensive test suite
- Usage examples
- Management command for testing
- Detailed documentation
- Type hints and docstrings

## Installation & Setup

### 1. Install the Package
```bash
pip install django-sslcommerz
# Or with DRF support
pip install django-sslcommerz[drf]
```

### 2. Add to Django Settings
```python
INSTALLED_APPS = [
    # ... your apps
    'sslcommerz',
]

SSLCOMMERZ = {
    'STORE_ID': 'your_store_id',
    'STORE_PASSWORD': 'your_store_password',
    'IS_SANDBOX': True,
    'SUCCESS_URL': 'https://yourdomain.com/payment/success/',
    'FAIL_URL': 'https://yourdomain.com/payment/fail/',
    'CANCEL_URL': 'https://yourdomain.com/payment/cancel/',
    'IPN_URL': 'https://yourdomain.com/payment/ipn/',
}
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Test Configuration
```bash
python manage.py test_sslcommerz
python manage.py test_sslcommerz --test-payment --amount 100
```

## Key Components

### Configuration System (`config.py`)
- Supports Django settings and environment variables
- Automatic URL generation for sandbox/production
- Configuration validation on startup
- Thread-safe global configuration instance

### API Client (`client.py`)
- Full SSLCOMMERZ API v4 implementation
- Request/response logging
- Automatic data validation
- Error handling with custom exceptions
- Support for all payment parameters

### IPN Handler (`handlers.py`)
- Automatic transaction validation
- Django signals integration
- Configurable validation behavior
- Hash verification support

### Models (`models.py`)
- Transaction tracking with full audit trail
- Refund transaction support
- User relationship integration
- JSON field for metadata storage
- Status management methods

### Django REST Framework (`drf.py`)
- Optional DRF integration
- API endpoints for payment operations
- Serializers for data validation
- ViewSets with authentication

## Extension Points

### 1. Django Signals
```python
from django.dispatch import receiver
from sslcommerz.signals import payment_successful

@receiver(payment_successful)
def handle_payment_success(sender, **kwargs):
    # Your custom logic here
    pass
```

### 2. Custom IPN Views
```python
from sslcommerz.views import BaseIPNView

class CustomIPNView(BaseIPNView):
    def handle_ipn_success(self, result):
        # Your business logic
        pass
```

### 3. Custom Configuration
```python
from sslcommerz.config import SSLCommerzConfig
from sslcommerz.client import SSLCommerzClient

custom_config = SSLCommerzConfig()
client = SSLCommerzClient(config=custom_config)
```

## Testing

### Run Test Suite
```bash
python manage.py test
```

### Test Configuration
```bash
python manage.py test_sslcommerz
```

### Test Payment Flow
```bash
python manage.py test_sslcommerz --test-payment --amount 100
```

## Security Considerations

1. **Store credentials securely** - Use environment variables in production
2. **Validate IPN data** - Always validate transactions with SSLCOMMERZ
3. **Use HTTPS** - All callback URLs must use HTTPS in production
4. **Verify amounts** - Always verify transaction amounts match your records
5. **Log transactions** - Keep audit trail of all payment operations

## Production Checklist

- [ ] Store credentials configured via environment variables
- [ ] IS_SANDBOX set to False
- [ ] All callback URLs use HTTPS
- [ ] IPN endpoint is accessible from SSLCOMMERZ servers
- [ ] Logging configured for production
- [ ] Error monitoring in place
- [ ] Database backups enabled
- [ ] SSL certificate valid

## Troubleshooting

### Common Issues

1. **Configuration Errors**
   ```bash
   python manage.py test_sslcommerz
   ```

2. **IPN Not Working**
   - Check IPN URL accessibility
   - Verify CSRF exemption
   - Check server logs

3. **Payment Initiation Fails**
   - Verify store credentials
   - Check network connectivity
   - Review API request logs

### Debug Mode
```python
SSLCOMMERZ = {
    # ... other settings
    'LOG_REQUESTS': True,  # Enable request logging
}
```

## Support & Contributing

- **Documentation**: [Link to docs]
- **Issues**: [Link to issues]
- **Contributing**: [Link to contributing guide]
- **License**: MIT License

## Version History

- **v1.0.0**: Initial release with full API v4 support
  - Payment initiation
  - IPN handling
  - Transaction validation
  - Refund processing
  - Django and DRF integration
  - Comprehensive test suite

## API Reference

See `examples.py` for comprehensive usage examples covering all features.
