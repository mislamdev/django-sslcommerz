# Examples

This page provides comprehensive examples for using Django SSLCOMMERZ in various scenarios.

## Basic Payment Flow

### Simple Payment Initiation

```python
from django.shortcuts import render, redirect
from sslcommerz.client import SSLCommerzClient
from sslcommerz.utils import generate_transaction_id
from sslcommerz.models import Transaction

def simple_payment(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        
        # Generate unique transaction ID
        tran_id = generate_transaction_id('SIMPLE')
        
        # Basic payment data
        payment_data = {
            'total_amount': amount,
            'currency': 'BDT',
            'tran_id': tran_id,
            'product_name': 'Simple Product',
            'cus_name': 'Customer Name',
            'cus_email': 'customer@example.com',
            'cus_phone': '01700000000',
        }
        
        # Create transaction record
        Transaction.objects.create(
            tran_id=tran_id,
            amount=amount,
            currency='BDT',
            customer_name=payment_data['cus_name'],
            customer_email=payment_data['cus_email'],
            customer_phone=payment_data['cus_phone'],
            product_name=payment_data['product_name'],
        )
        
        # Initiate payment
        client = SSLCommerzClient()
        response = client.initiate_payment(payment_data)
        
        return redirect(response['GatewayPageURL'])
    
    return render(request, 'payment_form.html')
```

## Advanced Payment Integration

### E-commerce Integration

```python
from django.contrib.auth.decorators import login_required
from django.db import transaction
from myapp.models import Order, Product

@login_required
@transaction.atomic
def checkout_payment(request, order_id):
    """Complete checkout with SSLCOMMERZ payment."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status != 'PENDING':
        return redirect('order_detail', order_id=order.id)
    
    # Generate transaction ID
    tran_id = generate_transaction_id(f'ORDER_{order.id}')
    
    # Prepare detailed payment data
    payment_data = {
        'total_amount': float(order.total_amount),
        'currency': 'BDT',
        'tran_id': tran_id,
        
        # Product information
        'product_name': f'Order #{order.id}',
        'product_category': 'goods',
        'product_profile': 'general',
        'product_amount': float(order.subtotal),
        'vat': float(order.tax_amount),
        'discount_amount': float(order.discount_amount),
        
        # Customer information
        'cus_name': order.billing_name,
        'cus_email': order.billing_email,
        'cus_phone': order.billing_phone,
        'cus_add1': order.billing_address,
        'cus_city': order.billing_city,
        'cus_country': 'Bangladesh',
        
        # Shipping information
        'ship_name': order.shipping_name,
        'ship_add1': order.shipping_address,
        'ship_city': order.shipping_city,
        'ship_country': 'Bangladesh',
        
        # Custom values for tracking
        'value_a': str(order.id),
        'value_b': order.order_number,
        'value_c': request.user.id if request.user.is_authenticated else '',
    }
    
    # Create SSLCOMMERZ transaction
    sslcommerz_transaction = Transaction.objects.create(
        tran_id=tran_id,
        amount=payment_data['total_amount'],
        currency=payment_data['currency'],
        customer_name=payment_data['cus_name'],
        customer_email=payment_data['cus_email'],
        customer_phone=payment_data['cus_phone'],
        product_name=payment_data['product_name'],
        user=request.user,
        metadata={'order_id': order.id}
    )
    
    # Update order with transaction reference
    order.sslcommerz_transaction = sslcommerz_transaction
    order.save()
    
    # Initiate payment
    client = SSLCommerzClient()
    response = client.initiate_payment(payment_data)
    
    # Save gateway response
    sslcommerz_transaction.gateway_response = response
    sslcommerz_transaction.save()
    
    return redirect(response['GatewayPageURL'])
```

## IPN Handling Examples

### Custom IPN Handler with Business Logic

```python
from sslcommerz.views import BaseIPNView
from django.core.mail import send_mail
from django.contrib.auth.models import User
from myapp.models import Order

class EcommerceIPNView(BaseIPNView):
    """Custom IPN handler for e-commerce platform."""
    
    def handle_ipn_success(self, result):
        """Process successful payment."""
        tran_id = result['tran_id']
        amount = float(result['amount'])
        
        try:
            # Get transaction and related order
            transaction = Transaction.objects.get(tran_id=tran_id)
            order_id = transaction.metadata.get('order_id')
            
            if order_id:
                order = Order.objects.get(id=order_id)
                self.process_successful_order(order, transaction, result)
                
        except (Transaction.DoesNotExist, Order.DoesNotExist):
            logger.error(f"Order not found for transaction: {tran_id}")
    
    def process_successful_order(self, order, transaction, ipn_data):
        """Process successful order payment."""
        # Update order status
        order.status = 'PAID'
        order.payment_method = 'SSLCOMMERZ'
        order.payment_reference = transaction.bank_tran_id
        order.paid_at = timezone.now()
        order.save()
        
        # Update inventory
        self.update_inventory(order)
        
        # Send confirmation email
        self.send_order_confirmation(order)
        
        # Create invoice
        self.create_invoice(order)
        
        # Process loyalty points
        self.award_loyalty_points(order)
    
    def update_inventory(self, order):
        """Update product inventory."""
        for item in order.items.all():
            product = item.product
            product.stock_quantity -= item.quantity
            product.save()
    
    def send_order_confirmation(self, order):
        """Send order confirmation email."""
        send_mail(
            subject=f'Order Confirmation #{order.order_number}',
            message=f'Your order has been confirmed and payment received.',
            from_email='noreply@yourstore.com',
            recipient_list=[order.billing_email],
        )
    
    def create_invoice(self, order):
        """Generate invoice for the order."""
        # Implement invoice generation logic
        pass
    
    def award_loyalty_points(self, order):
        """Award loyalty points to customer."""
        if order.user:
            points = int(order.total_amount * 0.01)  # 1% as points
            order.user.profile.loyalty_points += points
            order.user.profile.save()
```

## Django REST Framework Examples

### Payment API Views

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from sslcommerz.drf import PaymentInitiationSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_payment(request):
    """API endpoint to create a payment session."""
    serializer = PaymentInitiationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Add user information
        payment_data = serializer.validated_data
        payment_data.update({
            'cus_name': request.user.get_full_name() or request.user.username,
            'cus_email': request.user.email,
        })
        
        try:
            # Create transaction
            transaction = Transaction.objects.create(
                tran_id=payment_data['tran_id'],
                amount=payment_data['total_amount'],
                currency=payment_data['currency'],
                customer_name=payment_data['cus_name'],
                customer_email=payment_data['cus_email'],
                customer_phone=payment_data['cus_phone'],
                user=request.user
            )
            
            # Initiate payment
            client = SSLCommerzClient()
            response = client.initiate_payment(payment_data)
            
            transaction.gateway_response = response
            transaction.save()
            
            return Response({
                'status': 'success',
                'transaction_id': transaction.tran_id,
                'gateway_url': response.get('GatewayPageURL'),
                'expires_at': response.get('expired_time')
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'status': 'error',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_payment_status(request, tran_id):
    """Check payment status via API."""
    try:
        transaction = Transaction.objects.get(
            tran_id=tran_id,
            user=request.user
        )
        
        return Response({
            'transaction_id': transaction.tran_id,
            'status': transaction.status,
            'amount': str(transaction.amount),
            'currency': transaction.currency,
            'is_successful': transaction.is_successful,
            'created_at': transaction.created_at.isoformat(),
        })
        
    except Transaction.DoesNotExist:
        return Response({
            'error': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)
```

## Signal Usage Examples

### Django Signals Integration

```python
from django.dispatch import receiver
from sslcommerz.signals import payment_successful, payment_failed
from django.core.mail import send_mail
from myapp.models import UserProfile

@receiver(payment_successful)
def handle_successful_payment(sender, **kwargs):
    """Handle successful payment events."""
    tran_id = kwargs['tran_id']
    amount = kwargs['amount']
    ipn_data = kwargs['ipn_data']
    
    try:
        transaction = Transaction.objects.get(tran_id=tran_id)
        
        # Update user credits if applicable
        if transaction.user:
            profile = UserProfile.objects.get(user=transaction.user)
            profile.credits += float(amount)
            profile.save()
        
        # Send success notification
        send_mail(
            subject='Payment Successful',
            message=f'Your payment of {amount} BDT has been processed successfully.',
            from_email='noreply@yoursite.com',
            recipient_list=[transaction.customer_email],
        )
        
        # Log for analytics
        from myapp.analytics import track_payment
        track_payment(tran_id, amount, 'success')
        
    except Exception as e:
        logger.error(f"Error in payment success handler: {e}")

@receiver(payment_failed)
def handle_failed_payment(sender, **kwargs):
    """Handle failed payment events."""
    tran_id = kwargs['tran_id']
    reason = kwargs.get('reason', 'Unknown')
    
    try:
        transaction = Transaction.objects.get(tran_id=tran_id)
        
        # Send failure notification
        send_mail(
            subject='Payment Failed',
            message=f'Your payment failed. Reason: {reason}',
            from_email='noreply@yoursite.com',
            recipient_list=[transaction.customer_email],
        )
        
        # Log for analytics
        from myapp.analytics import track_payment
        track_payment(tran_id, transaction.amount, 'failed', reason)
        
    except Exception as e:
        logger.error(f"Error in payment failure handler: {e}")
```

## Transaction Validation Examples

### Manual Transaction Validation

```python
from sslcommerz.client import SSLCommerzClient

def validate_pending_transactions():
    """Validate pending transactions."""
    client = SSLCommerzClient()
    pending_transactions = Transaction.objects.filter(
        status='PENDING',
        created_at__gte=timezone.now() - timedelta(hours=24)
    )
    
    for transaction in pending_transactions:
        try:
            result = client.validate_transaction(
                transaction.val_id or transaction.tran_id,
                str(transaction.amount)
            )
            
            if result.get('status') == 'VALID':
                transaction.mark_as_successful()
                logger.info(f"Transaction {transaction.tran_id} validated successfully")
            elif result.get('status') in ['FAILED', 'CANCELLED']:
                transaction.mark_as_failed('Validation failed')
                logger.warning(f"Transaction {transaction.tran_id} validation failed")
                
        except Exception as e:
            logger.error(f"Error validating transaction {transaction.tran_id}: {e}")
```

## Refund Examples

### Processing Refunds

```python
from sslcommerz.client import SSLCommerzClient
from sslcommerz.models import RefundTransaction

def process_refund(transaction_id, refund_amount, reason):
    """Process a refund for a transaction."""
    try:
        transaction = Transaction.objects.get(tran_id=transaction_id)
        
        if not transaction.can_be_refunded:
            raise ValueError("Transaction cannot be refunded")
        
        # Prepare refund data
        refund_data = {
            'bank_tran_id': transaction.bank_tran_id,
            'refund_amount': refund_amount,
            'refund_remarks': reason,
            'refe_id': f'REF_{transaction.tran_id}_{timezone.now().strftime("%Y%m%d%H%M%S")}'
        }
        
        # Process refund with SSLCOMMERZ
        client = SSLCommerzClient()
        refund_result = client.process_refund(refund_data)
        
        # Create refund record
        refund_transaction = RefundTransaction.objects.create(
            original_transaction=transaction,
            refund_id=refund_data['refe_id'],
            refund_amount=refund_amount,
            refund_reason=reason,
            gateway_response=refund_result,
            status='SUCCESS' if refund_result.get('status') == 'SUCCESS' else 'FAILED'
        )
        
        # Update original transaction if refund successful
        if refund_result.get('status') == 'SUCCESS':
            transaction.status = 'REFUNDED'
            transaction.save()
        
        return refund_transaction
        
    except Exception as e:
        logger.error(f"Refund processing failed: {e}")
        raise
```

## Testing Examples

### Unit Testing with Mock

```python
import unittest.mock as mock
from django.test import TestCase
from sslcommerz.client import SSLCommerzClient

class PaymentTestCase(TestCase):
    
    @mock.patch('sslcommerz.client.requests.Session.post')
    def test_payment_initiation(self, mock_post):
        """Test payment initiation with mocked response."""
        # Mock SSLCOMMERZ response
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            'status': 'SUCCESS',
            'GatewayPageURL': 'https://sandbox.sslcommerz.com/test',
            'sessionkey': 'test_session_key'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test payment initiation
        client = SSLCommerzClient()
        payment_data = {
            'total_amount': 100.00,
            'currency': 'BDT',
            'tran_id': 'TEST_123',
            'cus_name': 'Test User',
            'cus_email': 'test@example.com',
            'cus_phone': '01700000000'
        }
        
        result = client.initiate_payment(payment_data)
        
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertIn('GatewayPageURL', result)
```

## Production Best Practices

### Error Handling

```python
from sslcommerz.exceptions import SSLCommerzError, SSLCommerzAPIError

def robust_payment_initiation(payment_data):
    """Payment initiation with comprehensive error handling."""
    try:
        client = SSLCommerzClient()
        response = client.initiate_payment(payment_data)
        
        return {
            'success': True,
            'gateway_url': response['GatewayPageURL'],
            'session_key': response.get('sessionkey')
        }
        
    except SSLCommerzValidationError as e:
        # Handle validation errors
        return {
            'success': False,
            'error_type': 'validation',
            'message': str(e)
        }
        
    except SSLCommerzAPIError as e:
        # Handle API errors
        return {
            'success': False,
            'error_type': 'api',
            'message': str(e)
        }
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected payment error: {e}")
        return {
            'success': False,
            'error_type': 'unexpected',
            'message': 'An unexpected error occurred'
        }
```
