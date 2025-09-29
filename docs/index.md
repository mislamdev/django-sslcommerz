# Django SSLCOMMERZ Documentation

Welcome to the Django SSLCOMMERZ documentation! This package provides a comprehensive integration with the SSLCOMMERZ Payment Gateway API v4 for Django applications.

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
quickstart
configuration
api_reference
examples
deployment
contributing
changelog
```

## Overview

Django SSLCOMMERZ is a production-ready Django package that provides seamless integration with Bangladesh's leading payment gateway, SSLCOMMERZ. It supports the complete payment workflow including payment initiation, IPN handling, transaction validation, and refunds.

### Key Features

- **Complete API Coverage**: Payment initiation, IPN handling, transaction validation, and refunds
- **Django Integration**: Models, views, admin interface, and management commands
- **Optional DRF Support**: REST API endpoints and serializers when Django REST Framework is installed
- **Production Ready**: Robust error handling, logging, and security features
- **Flexible Configuration**: Support for Django settings and environment variables
- **Multi-Environment**: Easy switching between sandbox and production environments

### Quick Example

```python
from sslcommerz.client import SSLCommerzClient

# Initialize client
client = SSLCommerzClient()

# Initiate payment
payment_data = {
    'total_amount': 1000.00,
    'currency': 'BDT',
    'tran_id': 'unique_transaction_id',
    'cus_name': 'Customer Name',
    'cus_email': 'customer@example.com',
    'cus_phone': '01700000000',
}

response = client.initiate_payment(payment_data)
# Redirect user to response['GatewayPageURL']
```

## Getting Help

- **Documentation**: This comprehensive guide
- **GitHub Issues**: [Report bugs or request features](https://github.com/your-username/django-sslcommerz/issues)
- **GitHub Discussions**: [Ask questions and get help](https://github.com/your-username/django-sslcommerz/discussions)

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
