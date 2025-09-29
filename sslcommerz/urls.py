"""
URL configuration for SSLCOMMERZ package.
"""
from django.urls import path, include

from .views import IPNView, IPNJsonView, simple_ipn_view, TransactionStatusView

# Basic URL patterns
urlpatterns = [
    path("ipn/", IPNView.as_view(), name="sslcommerz_ipn"),
    path("ipn/json/", IPNJsonView.as_view(), name="sslcommerz_ipn_json"),
    path("ipn/simple/", simple_ipn_view, name="sslcommerz_ipn_simple"),
    path(
        "status/<str:tran_id>/",
        TransactionStatusView.as_view(),
        name="sslcommerz_status",
    ),
]

# Add DRF URLs if available
try:
    from rest_framework.routers import DefaultRouter
    from .drf import TransactionViewSet, PaymentViewSet, DRF_AVAILABLE

    if DRF_AVAILABLE:
        router = DefaultRouter()
        router.register(r"transactions", TransactionViewSet)
        router.register(r"payments", PaymentViewSet, basename="payment")

        urlpatterns += [
            path("api/", include(router.urls)),
        ]

except ImportError:
    # DRF not available, skip API routes
    pass

app_name = "sslcommerz"
