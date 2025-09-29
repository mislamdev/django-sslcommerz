# API Reference

This section provides detailed documentation for all Django SSLCOMMERZ classes, methods, and functions.

## Core Components

```{eval-rst}
.. automodule:: sslcommerz
   :members:
   :undoc-members:
   :show-inheritance:
```

## Client

```{eval-rst}
.. automodule:: sslcommerz.client
   :members:
   :undoc-members:
   :show-inheritance:
```

### SSLCommerzClient

```{eval-rst}
.. autoclass:: sslcommerz.client.SSLCommerzClient
   :members:
   :undoc-members:
   :show-inheritance:
```

## Configuration

```{eval-rst}
.. automodule:: sslcommerz.config
   :members:
   :undoc-members:
   :show-inheritance:
```

### SSLCommerzConfig

```{eval-rst}
.. autoclass:: sslcommerz.config.SSLCommerzConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

## Models

```{eval-rst}
.. automodule:: sslcommerz.models
   :members:
   :undoc-members:
   :show-inheritance:
```

### Transaction

```{eval-rst}
.. autoclass:: sslcommerz.models.Transaction
   :members:
   :undoc-members:
   :show-inheritance:
```

### RefundTransaction

```{eval-rst}
.. autoclass:: sslcommerz.models.RefundTransaction
   :members:
   :undoc-members:
   :show-inheritance:
```

## Views

```{eval-rst}
.. automodule:: sslcommerz.views
   :members:
   :undoc-members:
   :show-inheritance:
```

### BaseIPNView

```{eval-rst}
.. autoclass:: sslcommerz.views.BaseIPNView
   :members:
   :undoc-members:
   :show-inheritance:
```

## IPN Handlers

```{eval-rst}
.. automodule:: sslcommerz.handlers
   :members:
   :undoc-members:
   :show-inheritance:
```

### IPNHandler

```{eval-rst}
.. autoclass:: sslcommerz.handlers.IPNHandler
   :members:
   :undoc-members:
   :show-inheritance:
```

## Django REST Framework (Optional)

```{eval-rst}
.. automodule:: sslcommerz.drf
   :members:
   :undoc-members:
   :show-inheritance:
```

### Serializers

```{eval-rst}
.. autoclass:: sslcommerz.drf.TransactionSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: sslcommerz.drf.PaymentInitiationSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: sslcommerz.drf.RefundSerializer
   :members:
   :undoc-members:
   :show-inheritance:
```

### ViewSets

```{eval-rst}
.. autoclass:: sslcommerz.drf.TransactionViewSet
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: sslcommerz.drf.PaymentViewSet
   :members:
   :undoc-members:
   :show-inheritance:
```

## Utilities

```{eval-rst}
.. automodule:: sslcommerz.utils
   :members:
   :undoc-members:
   :show-inheritance:
```

## Exceptions

```{eval-rst}
.. automodule:: sslcommerz.exceptions
   :members:
   :undoc-members:
   :show-inheritance:
```

### Exception Hierarchy

- `SSLCommerzError` - Base exception for all SSLCOMMERZ related errors
  - `SSLCommerzConfigError` - Configuration errors
  - `SSLCommerzAPIError` - API request/response errors
  - `SSLCommerzValidationError` - Data validation errors
  - `SSLCommerzIPNError` - IPN processing errors

## Signals

```{eval-rst}
.. automodule:: sslcommerz.signals
   :members:
   :undoc-members:
   :show-inheritance:
```

### Available Signals

- `ipn_received` - Sent when an IPN is received (before validation)
- `payment_successful` - Sent when a payment is successful and validated
- `payment_failed` - Sent when a payment fails or validation fails
- `refund_processed` - Sent when a refund is processed
- `pre_payment_initiation` - Sent before payment initiation
- `post_payment_initiation` - Sent after payment initiation

## Admin

```{eval-rst}
.. automodule:: sslcommerz.admin
   :members:
   :undoc-members:
   :show-inheritance:
```

## Management Commands

### test_sslcommerz

Test SSLCOMMERZ configuration and connectivity.

```bash
python manage.py test_sslcommerz [options]
```

**Options:**
- `--test-payment` - Test payment initiation (sandbox only)
- `--validate-transaction ID` - Validate a specific transaction
- `--amount AMOUNT` - Amount for test payment (default: 10.0)

**Examples:**
```bash
# Basic configuration test
python manage.py test_sslcommerz

# Test payment initiation
python manage.py test_sslcommerz --test-payment --amount 100

# Validate specific transaction
python manage.py test_sslcommerz --validate-transaction TXN_123456
```
