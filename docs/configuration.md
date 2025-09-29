# Configuration

This page covers all configuration options available in Django SSLCOMMERZ.

## Django Settings Configuration

Configure SSLCOMMERZ in your Django `settings.py`:

```python
SSLCOMMERZ = {
    # Required Settings
    'STORE_ID': 'your_store_id_here',
    'STORE_PASSWORD': 'your_store_password_here',
    
    # Environment Settings
    'IS_SANDBOX': True,  # False for production
    
    # Payment URLs (Required)
    'SUCCESS_URL': 'https://yourdomain.com/payment/success/',
    'FAIL_URL': 'https://yourdomain.com/payment/fail/',
    'CANCEL_URL': 'https://yourdomain.com/payment/cancel/',
    'IPN_URL': 'https://yourdomain.com/payment/ipn/',
    
    # Optional Settings
    'TIMEOUT': 30,                    # API request timeout in seconds
    'VERIFY_SSL': True,               # SSL verification for API requests
    'LOG_REQUESTS': False,            # Log API requests (for debugging)
    'AUTO_VALIDATE_IPN': True,        # Automatically validate IPN
    'STORE_NAME': 'Your Store Name',  # Optional store name
    'CURRENCY': 'BDT',               # Default currency
}
```

## Environment Variables

Environment variables take precedence over Django settings:

```bash
# Required
SSLCOMMERZ_STORE_ID=your_store_id
SSLCOMMERZ_STORE_PASSWORD=your_store_password

# Environment
SSLCOMMERZ_IS_SANDBOX=True

# URLs
SSLCOMMERZ_SUCCESS_URL=https://yourdomain.com/payment/success/
SSLCOMMERZ_FAIL_URL=https://yourdomain.com/payment/fail/
SSLCOMMERZ_CANCEL_URL=https://yourdomain.com/payment/cancel/
SSLCOMMERZ_IPN_URL=https://yourdomain.com/payment/ipn/

# Optional
SSLCOMMERZ_TIMEOUT=30
SSLCOMMERZ_VERIFY_SSL=True
SSLCOMMERZ_LOG_REQUESTS=False
SSLCOMMERZ_AUTO_VALIDATE_IPN=True
```

## Configuration Reference

### Required Settings

| Setting | Type | Description |
|---------|------|-------------|
| `STORE_ID` | string | Your SSLCOMMERZ store ID |
| `STORE_PASSWORD` | string | Your SSLCOMMERZ store password |

### Environment Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `IS_SANDBOX` | boolean | `True` | Use sandbox environment |

### URL Settings

| Setting | Type | Description |
|---------|------|-------------|
| `SUCCESS_URL` | string | URL for successful payments |
| `FAIL_URL` | string | URL for failed payments |
| `CANCEL_URL` | string | URL for cancelled payments |
| `IPN_URL` | string | URL for IPN callbacks |

### Optional Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `TIMEOUT` | integer | `30` | API request timeout (seconds) |
| `VERIFY_SSL` | boolean | `True` | SSL certificate verification |
| `LOG_REQUESTS` | boolean | `False` | Log API requests/responses |
| `AUTO_VALIDATE_IPN` | boolean | `True` | Auto-validate IPN data |
| `STORE_NAME` | string | `None` | Optional store name |
| `CURRENCY` | string | `'BDT'` | Default currency |

## Multiple Store Configuration

For applications with multiple SSLCOMMERZ stores:

```python
from sslcommerz.config import SSLCommerzConfig
from sslcommerz.client import SSLCommerzClient

# Create custom configuration
custom_config = SSLCommerzConfig()
custom_config._config.update({
    'STORE_ID': 'secondary_store_id',
    'STORE_PASSWORD': 'secondary_store_password',
    'IS_SANDBOX': False,
})

# Use custom configuration
client = SSLCommerzClient(config=custom_config)
```

## Validation

The package automatically validates configuration on startup. To manually validate:

```python
from sslcommerz.config import validate_config

try:
    validate_config()
    print("Configuration is valid")
except Exception as e:
    print(f"Configuration error: {e}")
```

## Production Configuration

### Security Checklist

- [ ] Use environment variables for sensitive data
- [ ] Set `IS_SANDBOX=False` for production
- [ ] Use HTTPS for all callback URLs
- [ ] Verify SSL certificates (`VERIFY_SSL=True`)
- [ ] Disable request logging (`LOG_REQUESTS=False`)

### Example Production Settings

```python
# Production settings.py
import os
from decouple import config

SSLCOMMERZ = {
    'STORE_ID': config('SSLCOMMERZ_STORE_ID'),
    'STORE_PASSWORD': config('SSLCOMMERZ_STORE_PASSWORD'),
    'IS_SANDBOX': config('SSLCOMMERZ_IS_SANDBOX', default=False, cast=bool),
    'SUCCESS_URL': config('SSLCOMMERZ_SUCCESS_URL'),
    'FAIL_URL': config('SSLCOMMERZ_FAIL_URL'),
    'CANCEL_URL': config('SSLCOMMERZ_CANCEL_URL'),
    'IPN_URL': config('SSLCOMMERZ_IPN_URL'),
    'VERIFY_SSL': True,
    'LOG_REQUESTS': False,
}
```

## Configuration Testing

Use the management command to test your configuration:

```bash
# Basic configuration test
python manage.py test_sslcommerz

# Test with payment initiation (sandbox only)
python manage.py test_sslcommerz --test-payment --amount 100

# Check production readiness
python manage.py test_sslcommerz --production-check
```
