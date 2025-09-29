# Django SSLCOMMERZ

A production-ready Django package for integrating with SSLCOMMERZ Payment Gateway API v4.

## Features

- **Production Ready**: Robust error handling, logging, and configuration management
- **Django Integration**: Works as a Django app with proper settings integration
- **Optional DRF Support**: Includes REST framework serializers and viewsets when DRF is installed
- **Flexible Configuration**: Supports Django settings and environment variables
- **Complete API Coverage**: Payment initiation, IPN handling, transaction validation, and refunds
- **Sandbox & Live Support**: Easy switching between environments
- **Extensible**: Clear hooks for custom business logic

## Installation

```bash
pip install django-sslcommerz
```

For Django REST Framework support:
```bash
pip install django-sslcommerz[drf]
```

## Quick Setup

1. Add to your Django `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... your apps
    'sslcommerz',
]
```

2. Add SSLCOMMERZ settings:

```python
# settings.py
SSLCOMMERZ = {
    'STORE_ID': 'your_store_id',
    'STORE_PASSWORD': 'your_store_password',
    'IS_SANDBOX': True,  # Set to False for production
    'SUCCESS_URL': 'https://yoursite.com/payment/success/',
    'FAIL_URL': 'https://yoursite.com/payment/fail/',
    'CANCEL_URL': 'https://yoursite.com/payment/cancel/',
    'IPN_URL': 'https://yoursite.com/payment/ipn/',
}
```

3. Include URLs (optional, for DRF endpoints):

```python
# urls.py
urlpatterns = [
    # ... your urls
    path('api/payments/', include('sslcommerz.urls')),
]
```

## Environment Variables

You can also configure using environment variables (will override settings):

```env
SSLCOMMERZ_STORE_ID=your_store_id
SSLCOMMERZ_STORE_PASSWORD=your_store_password
SSLCOMMERZ_IS_SANDBOX=True
SSLCOMMERZ_SUCCESS_URL=https://yoursite.com/payment/success/
SSLCOMMERZ_FAIL_URL=https://yoursite.com/payment/fail/
SSLCOMMERZ_CANCEL_URL=https://yoursite.com/payment/cancel/
SSLCOMMERZ_IPN_URL=https://yoursite.com/payment/ipn/
```

## Usage Examples

### Basic Payment Initiation

```python
from sslcommerz.client import SSLCommerzClient

client = SSLCommerzClient()

payment_data = {
    'total_amount': 1000.00,
    'currency': 'BDT',
    'tran_id': 'unique_transaction_id',
    'product_name': 'Test Product',
    'product_category': 'goods',
    'product_profile': 'general',
    'cus_name': 'Customer Name',
    'cus_email': 'customer@example.com',
    'cus_phone': '01700000000',
    'cus_add1': 'Customer Address',
    'cus_city': 'Dhaka',
    'cus_country': 'Bangladesh',
}

response = client.initiate_payment(payment_data)
if response['status'] == 'SUCCESS':
    # Redirect user to response['GatewayPageURL']
    pass
```

### IPN Handling

```python
from sslcommerz.handlers import handle_ipn

def payment_ipn_view(request):
    if request.method == 'POST':
        result = handle_ipn(request.POST)
        if result['valid']:
            # Payment successful, update your models
            pass
    return HttpResponse('OK')
```

### Transaction Validation

```python
from sslcommerz.client import SSLCommerzClient

client = SSLCommerzClient()
validation_result = client.validate_transaction('transaction_id', 'amount')

if validation_result['status'] == 'VALID':
    # Transaction is valid
    pass
```

## Documentation

For detailed documentation, examples, and API reference, visit: [Documentation Link]

## License

MIT License
