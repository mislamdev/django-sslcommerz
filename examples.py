"""
Comprehensive usage examples for Django SSLCOMMERZ package.
"""

# ============================================================================
# Example 1: Basic Payment Initiation in Django Views
# ============================================================================

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from sslcommerz.client import SSLCommerzClient
from sslcommerz.utils import generate_transaction_id
from sslcommerz.models import Transaction
from sslcommerz.exceptions import SSLCommerzError


@login_required
def initiate_payment(request):
    """Initiate a payment for the logged-in user."""
    if request.method == "POST":
        # Get payment details from form
        amount = float(request.POST.get("amount", 0))
        product_name = request.POST.get("product_name", "")

        if amount <= 0:
            return JsonResponse({"error": "Invalid amount"}, status=400)

        # Generate unique transaction ID
        tran_id = generate_transaction_id("ORDER")

        # Prepare payment data
        payment_data = {
            "total_amount": amount,
            "currency": "BDT",
            "tran_id": tran_id,
            "product_name": product_name,
            "product_category": "goods",
            "product_profile": "general",
            # Customer information from user profile
            "cus_name": request.user.get_full_name() or request.user.username,
            "cus_email": request.user.email,
            "cus_phone": getattr(request.user, "phone", "01700000000"),
            "cus_add1": getattr(request.user, "address", "Dhaka"),
            "cus_city": "Dhaka",
            "cus_country": "Bangladesh",
        }

        try:
            # Create transaction record
            transaction = Transaction.objects.create(
                tran_id=tran_id,
                amount=amount,
                currency="BDT",
                customer_name=payment_data["cus_name"],
                customer_email=payment_data["cus_email"],
                customer_phone=payment_data["cus_phone"],
                product_name=product_name,
                user=request.user,
                status="PENDING",
            )

            # Initiate payment with SSLCOMMERZ
            client = SSLCommerzClient()
            response = client.initiate_payment(payment_data)

            # Update transaction with gateway response
            transaction.gateway_response = response
            transaction.save()

            # Redirect to payment gateway
            return redirect(response["GatewayPageURL"])

        except SSLCommerzError as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, "payment/initiate.html")


# ============================================================================
# Example 2: IPN Handler with Custom Business Logic
# ============================================================================

from sslcommerz.views import BaseIPNView
from django.contrib.auth.models import User
from myapp.models import Order  # Your custom order model


class CustomIPNView(BaseIPNView):
    """Custom IPN handler with business logic."""

    def handle_ipn_success(self, result):
        """Custom logic when IPN is successfully processed."""
        tran_id = result["tran_id"]
        amount = result["amount"]

        try:
            # Update your order model
            order = Order.objects.get(transaction_id=tran_id)
            order.status = "PAID"
            order.payment_completed_at = timezone.now()
            order.save()

            # Send confirmation email
            self.send_payment_confirmation_email(order)

            # Update inventory
            self.update_inventory(order)

        except Order.DoesNotExist:
            logger.warning(f"Order not found for transaction: {tran_id}")

    def handle_ipn_error(self, error_message):
        """Custom logic when IPN processing fails."""
        # Log error, send alert, etc.
        logger.error(f"IPN processing failed: {error_message}")
        # Send alert to admin
        self.send_admin_alert(error_message)

    def send_payment_confirmation_email(self, order):
        """Send payment confirmation email to customer."""
        # Implement email sending logic
        pass

    def update_inventory(self, order):
        """Update product inventory after successful payment."""
        # Implement inventory update logic
        pass

    def send_admin_alert(self, error_message):
        """Send alert to administrators."""
        # Implement admin notification logic
        pass


# ============================================================================
# Example 3: Django REST Framework API Views
# ============================================================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_initiate_payment(request):
    """API endpoint to initiate payment."""
    from sslcommerz.drf import PaymentInitiationSerializer

    serializer = PaymentInitiationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            client = SSLCommerzClient()

            # Add user information to payment data
            payment_data = serializer.validated_data
            payment_data.update(
                {
                    "cus_name": request.user.get_full_name() or request.user.username,
                    "cus_email": request.user.email,
                }
            )

            # Create transaction
            transaction = Transaction.objects.create(
                tran_id=payment_data["tran_id"],
                amount=payment_data["total_amount"],
                currency=payment_data["currency"],
                customer_name=payment_data["cus_name"],
                customer_email=payment_data["cus_email"],
                customer_phone=payment_data["cus_phone"],
                user=request.user,
            )

            # Initiate payment
            response = client.initiate_payment(payment_data)
            transaction.gateway_response = response
            transaction.save()

            return Response(
                {
                    "status": "success",
                    "transaction_id": transaction.tran_id,
                    "gateway_url": response.get("GatewayPageURL"),
                    "message": "Payment initiated successfully",
                }
            )

        except SSLCommerzError as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(
        {"status": "error", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


# ============================================================================
# Example 4: Using Django Signals for Custom Logic
# ============================================================================

from django.dispatch import receiver
from sslcommerz.signals import payment_successful, payment_failed


@receiver(payment_successful)
def handle_successful_payment(sender, **kwargs):
    """Handle successful payment events."""
    tran_id = kwargs["tran_id"]
    amount = kwargs["amount"]
    ipn_data = kwargs["ipn_data"]

    print(f"Payment successful: {tran_id} - {amount}")

    # Your custom logic here
    # - Send confirmation emails
    # - Update user credits
    # - Trigger fulfillment process
    # - Update analytics

    try:
        # Example: Update user credits
        transaction = Transaction.objects.get(tran_id=tran_id)
        if transaction.user:
            # Add credits to user account
            profile = transaction.user.profile
            profile.credits += float(amount)
            profile.save()

        # Example: Log to analytics
        from myapp.analytics import track_payment

        track_payment(tran_id, amount, "success")

    except Exception as e:
        logger.error(f"Error in payment success handler: {e}")


@receiver(payment_failed)
def handle_failed_payment(sender, **kwargs):
    """Handle failed payment events."""
    tran_id = kwargs["tran_id"]
    reason = kwargs.get("reason", "Unknown")

    print(f"Payment failed: {tran_id} - {reason}")

    # Your custom logic here
    # - Send failure notifications
    # - Log for analysis
    # - Retry logic if appropriate


# ============================================================================
# Example 5: Custom Management Command Usage
# ============================================================================

# Run configuration test
# python manage.py test_sslcommerz

# Test payment initiation in sandbox
# python manage.py test_sslcommerz --test-payment --amount 100

# Validate a specific transaction
# python manage.py test_sslcommerz --validate-transaction TXN_123456


# ============================================================================
# Example 6: Utility Functions Usage
# ============================================================================

from sslcommerz.utils import (
    generate_transaction_id,
    validate_amount,
    sanitize_customer_data,
    format_amount_for_display,
    is_production_ready,
)

# Generate unique transaction ID
tran_id = generate_transaction_id("ORD")  # ORD_20250929123456_ABC12345

# Validate amount
try:
    amount = validate_amount("100.50")  # Returns 100.5
except ValidationError as e:
    print(f"Invalid amount: {e}")

# Sanitize customer data
raw_data = {
    "cus_name": 'John & Jane <script>alert("XSS")</script>',
    "cus_email": "JOHN@EXAMPLE.COM",
    "total_amount": "100.50",
}
clean_data = sanitize_customer_data(raw_data)
# Result: {'cus_name': 'John and Jane', 'cus_email': 'john@example.com', 'total_amount': 100.5}

# Format amount for display
formatted = format_amount_for_display(1500.75, "BDT")  # "৳ 1,500.75"

# Check if ready for production
if is_production_ready():
    print("Configuration is ready for production")
else:
    print("Still in development/sandbox mode")


# ============================================================================
# Example 7: Advanced Configuration with Multiple Stores
# ============================================================================

from sslcommerz.config import SSLCommerzConfig
from sslcommerz.client import SSLCommerzClient

# Create custom configuration for different store
custom_config = SSLCommerzConfig()
custom_config._config.update(
    {
        "STORE_ID": "secondary_store_id",
        "STORE_PASSWORD": "secondary_store_password",
        "IS_SANDBOX": False,
    }
)

# Use custom configuration
client = SSLCommerzClient(config=custom_config)

# Now this client will use the custom store credentials


# ============================================================================
# Example 8: Error Handling Best Practices
# ============================================================================

from sslcommerz.exceptions import (
    SSLCommerzError,
    SSLCommerzAPIError,
    SSLCommerzValidationError,
)


def robust_payment_initiation(payment_data):
    """Example of robust error handling."""
    try:
        client = SSLCommerzClient()
        response = client.initiate_payment(payment_data)
        return {"success": True, "data": response}

    except SSLCommerzValidationError as e:
        # Data validation failed
        return {"success": False, "error": "validation", "message": str(e)}

    except SSLCommerzAPIError as e:
        # API request failed
        return {"success": False, "error": "api", "message": str(e)}

    except SSLCommerzError as e:
        # General SSLCOMMERZ error
        return {"success": False, "error": "general", "message": str(e)}

    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error in payment initiation: {e}")
        return {
            "success": False,
            "error": "unexpected",
            "message": "An unexpected error occurred",
        }


# ============================================================================
# Example 9: Testing Your Integration
# ============================================================================

# In your tests.py
from django.test import TestCase
from unittest.mock import patch, Mock
from sslcommerz.client import SSLCommerzClient


class PaymentIntegrationTest(TestCase):
    @patch("sslcommerz.client.requests.Session.post")
    def test_payment_flow(self, mock_post):
        """Test complete payment flow."""
        # Mock SSLCOMMERZ response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "GatewayPageURL": "https://sandbox.sslcommerz.com/test",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test payment initiation
        client = SSLCommerzClient()
        payment_data = {
            "total_amount": 100.00,
            "currency": "BDT",
            "tran_id": "TEST_123",
            "cus_name": "Test User",
            "cus_email": "test@example.com",
            "cus_phone": "01700000000",
        }

        result = client.initiate_payment(payment_data)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertIn("GatewayPageURL", result)
