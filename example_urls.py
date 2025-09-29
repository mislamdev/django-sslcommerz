"""
Example URL configuration for integrating SSLCOMMERZ into your Django project.
"""

# In your main urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Include SSLCOMMERZ URLs
    path("payments/", include("sslcommerz.urls")),
    # Your app URLs
    path("", include("myapp.urls")),
]

# ============================================================================
# In your app's urls.py (myapp/urls.py)
# ============================================================================

from django.urls import path
from . import views
from sslcommerz.views import IPNView

app_name = "myapp"

urlpatterns = [
    # Your regular views
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("cart/", views.cart, name="cart"),
    # Payment related views
    path("payment/initiate/", views.initiate_payment, name="initiate_payment"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/fail/", views.payment_fail, name="payment_fail"),
    path("payment/cancel/", views.payment_cancel, name="payment_cancel"),
    # IPN endpoint (you can use the built-in view or create custom)
    path("payment/ipn/", IPNView.as_view(), name="payment_ipn"),
    # Or use your custom IPN view:
    # path('payment/ipn/', views.CustomIPNView.as_view(), name='payment_ipn'),
]

# ============================================================================
# Example views.py for your app
# ============================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import View

from sslcommerz.client import SSLCommerzClient
from sslcommerz.utils import generate_transaction_id
from sslcommerz.models import Transaction
from sslcommerz.exceptions import SSLCommerzError
from sslcommerz.views import BaseIPNView


@login_required
def initiate_payment(request):
    """Initiate payment for a product or service."""
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        product_name = request.POST.get("product_name", "")

        if amount <= 0:
            messages.error(request, "Invalid amount")
            return redirect("myapp:cart")

        tran_id = generate_transaction_id("ORDER")

        payment_data = {
            "total_amount": amount,
            "currency": "BDT",
            "tran_id": tran_id,
            "product_name": product_name,
            "product_category": "goods",
            "product_profile": "general",
            "cus_name": request.user.get_full_name() or request.user.username,
            "cus_email": request.user.email,
            "cus_phone": "01700000000",  # Get from user profile
            "cus_add1": "Dhaka, Bangladesh",
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
            )

            # Initiate payment
            client = SSLCommerzClient()
            response = client.initiate_payment(payment_data)

            transaction.gateway_response = response
            transaction.save()

            return redirect(response["GatewayPageURL"])

        except SSLCommerzError as e:
            messages.error(request, f"Payment initiation failed: {e}")
            return redirect("myapp:cart")

    return render(request, "payment/initiate.html")


def payment_success(request):
    """Handle successful payment callback."""
    tran_id = request.GET.get("tran_id")

    if tran_id:
        try:
            transaction = Transaction.objects.get(tran_id=tran_id)
            # Additional verification can be done here
            return render(request, "payment/success.html", {"transaction": transaction})
        except Transaction.DoesNotExist:
            pass

    return render(request, "payment/success.html")


def payment_fail(request):
    """Handle failed payment callback."""
    tran_id = request.GET.get("tran_id")
    return render(request, "payment/fail.html", {"tran_id": tran_id})


def payment_cancel(request):
    """Handle cancelled payment callback."""
    tran_id = request.GET.get("tran_id")
    return render(request, "payment/cancel.html", {"tran_id": tran_id})


# Custom IPN View with business logic
class CustomIPNView(BaseIPNView):
    """Custom IPN handler with your business logic."""

    def handle_ipn_success(self, result):
        """Custom success handling."""
        tran_id = result["tran_id"]

        # Update your order/invoice status
        # Send confirmation emails
        # Update inventory
        # Add user credits, etc.

        # Example:
        try:
            transaction = Transaction.objects.get(tran_id=tran_id)
            if transaction.user:
                # Your custom business logic here
                self.process_order_completion(transaction)
        except Transaction.DoesNotExist:
            pass

    def process_order_completion(self, transaction):
        """Process order completion logic."""
        # Implement your business logic
        pass
