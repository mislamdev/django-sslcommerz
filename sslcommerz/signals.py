"""
Django signals for SSLCOMMERZ payment events.
These signals provide extension points for custom business logic.
"""
import django.dispatch

# Signal sent when an IPN is received (before validation)
ipn_received = django.dispatch.Signal()

# Signal sent when a payment is successful and validated
payment_successful = django.dispatch.Signal()

# Signal sent when a payment fails or validation fails
payment_failed = django.dispatch.Signal()

# Signal sent when a refund is processed
refund_processed = django.dispatch.Signal()

# Signal sent before payment initiation (for custom validation/modification)
pre_payment_initiation = django.dispatch.Signal()

# Signal sent after payment initiation (for logging/tracking)
post_payment_initiation = django.dispatch.Signal()
