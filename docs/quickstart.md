# Quick Start Guide

This guide will help you integrate SSLCOMMERZ payment gateway into your Django application in just a few steps.

## 1. Configuration

Configure SSLCOMMERZ in your Django settings:

```python
# settings.py
SSLCOMMERZ = {
    # Required Settings
    'STORE_ID': 'your_store_id_here',
    'STORE_PASSWORD': 'your_store_password_here',
    
    # Environment Settings
    'IS_SANDBOX': True,  # Set to False for production
    
    # Payment URLs (Required)
    'SUCCESS_URL': 'https://yourdomain.com/payment/success/',
    'FAIL_URL': 'https://yourdomain.com/payment/fail/',
    'CANCEL_URL': 'https://yourdomain.com/payment/cancel/',
    'IPN_URL': 'https://yourdomain.com/payment/ipn/',
    
    # Optional Settings
    'TIMEOUT': 30,
    'VERIFY_SSL': True,
    'LOG_REQUESTS': False,  # Set to True for debugging
}
```

## 2. Basic Payment Flow

### Step 1: Initiate Payment

```python
# views.py
from django.shortcuts import redirect
from sslcommerz.client import SSLCommerzClient
from sslcommerz.utils import generate_transaction_id
from sslcommerz.models import Transaction

def initiate_payment(request):
    # Generate unique transaction ID
    tran_id = generate_transaction_id('ORDER')
    
    # Prepare payment data
    payment_data = {
        'total_amount': 1000.00,
        'currency': 'BDT',
        'tran_id': tran_id,
        'product_name': 'Sample Product',
        'product_category': 'goods',
        'cus_name': 'John Doe',
        'cus_email': 'john@example.com',
        'cus_phone': '01700000000',
        'cus_add1': 'Dhaka, Bangladesh',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
    }
    
    # Create transaction record
    transaction = Transaction.objects.create(
        tran_id=tran_id,
        amount=payment_data['total_amount'],
        currency=payment_data['currency'],
        customer_name=payment_data['cus_name'],
        customer_email=payment_data['cus_email'],
        customer_phone=payment_data['cus_phone'],
        product_name=payment_data['product_name'],
        user=request.user if request.user.is_authenticated else None,
    )
    
    # Initiate payment with SSLCOMMERZ
    client = SSLCommerzClient()
    response = client.initiate_payment(payment_data)
    
    # Save gateway response
    transaction.gateway_response = response
    transaction.save()
    
    # Redirect to payment gateway
    return redirect(response['GatewayPageURL'])
```

### Step 2: Handle Payment Callbacks

```python
# views.py
from sslcommerz.views import BaseIPNView

class PaymentIPNView(BaseIPNView):
    """Custom IPN handler with your business logic."""
    
    def handle_ipn_success(self, result):
        """Called when payment is successful."""
        tran_id = result['tran_id']
        
        # Your business logic here
        # - Send confirmation emails
        # - Update order status
        # - Fulfill products/services
        
        try:
            transaction = Transaction.objects.get(tran_id=tran_id)
            # Process successful payment
            self.process_successful_payment(transaction)
        except Transaction.DoesNotExist:
            pass
    
    def process_successful_payment(self, transaction):
        """Process successful payment logic."""
        # Implement your business logic
        pass

def payment_success(request):
    """Handle successful payment callback."""
    tran_id = request.GET.get('tran_id')
    return render(request, 'payment/success.html', {'tran_id': tran_id})

def payment_fail(request):
    """Handle failed payment callback."""
    tran_id = request.GET.get('tran_id')
    return render(request, 'payment/fail.html', {'tran_id': tran_id})
```

### Step 3: URL Configuration

```python
# urls.py
from django.urls import path, include
from . import views
from .views import PaymentIPNView

urlpatterns = [
    # Your payment views
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),
    
    # IPN endpoint
    path('payment/ipn/', PaymentIPNView.as_view(), name='payment_ipn'),
    
    # Include SSLCOMMERZ URLs (optional)
    path('sslcommerz/', include('sslcommerz.urls')),
]
```

## 3. Django REST Framework Integration (Optional)

If you're using Django REST Framework:

```python
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sslcommerz.drf import PaymentInitiationSerializer

@api_view(['POST'])
def api_initiate_payment(request):
    """API endpoint to initiate payment."""
    serializer = PaymentInitiationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Process payment initiation
        client = SSLCommerzClient()
        response = client.initiate_payment(serializer.validated_data)
        
        return Response({
            'status': 'success',
            'gateway_url': response.get('GatewayPageURL'),
            'transaction_id': serializer.validated_data['tran_id']
        })
    
    return Response({
        'status': 'error',
        'errors': serializer.errors
    }, status=400)
```

## 4. Environment Variables (Optional)

You can also configure using environment variables:

```bash
# .env file
SSLCOMMERZ_STORE_ID=your_store_id
SSLCOMMERZ_STORE_PASSWORD=your_store_password
SSLCOMMERZ_IS_SANDBOX=True
SSLCOMMERZ_SUCCESS_URL=https://yourdomain.com/payment/success/
SSLCOMMERZ_FAIL_URL=https://yourdomain.com/payment/fail/
SSLCOMMERZ_CANCEL_URL=https://yourdomain.com/payment/cancel/
SSLCOMMERZ_IPN_URL=https://yourdomain.com/payment/ipn/
```

## 5. Testing

Test your integration:

```bash
# Test configuration
python manage.py test_sslcommerz

# Test payment initiation (sandbox only)
python manage.py test_sslcommerz --test-payment --amount 100

# Validate a specific transaction
python manage.py test_sslcommerz --validate-transaction TXN_123456
```

## Next Steps

- Read the [Configuration Guide](configuration.md) for detailed configuration options
- Check the [API Reference](api_reference.md) for complete API documentation
- See [Examples](examples.md) for more advanced usage patterns
- Review [Security Best Practices](deployment.md#security) before going to production
