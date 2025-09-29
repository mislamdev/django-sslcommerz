"""
Django REST Framework integration for SSLCOMMERZ (optional).
This module is only imported if DRF is available.
"""
import logging

try:
    from rest_framework import serializers, viewsets, status
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from rest_framework.permissions import IsAuthenticated

    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False

    # Create dummy classes to prevent import errors
    class serializers:
        class ModelSerializer:
            pass

        class Serializer:
            pass

        class CharField:
            pass

        class DecimalField:
            pass

        class EmailField:
            pass

        class DateTimeField:
            pass

        class JSONField:
            pass

        class URLField:
            pass

        class ValidationError(Exception):
            pass

    class viewsets:
        class ModelViewSet:
            pass

        class ViewSet:
            pass

    class Response:
        pass

    class IsAuthenticated:
        pass

    class status:
        HTTP_400_BAD_REQUEST = 400

    def action(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


logger = logging.getLogger(__name__)

if DRF_AVAILABLE:
    from .models import Transaction
    from .client import SSLCommerzClient
    from .handlers import handle_ipn
    from .exceptions import SSLCommerzError


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""

    class Meta:
        model = Transaction if DRF_AVAILABLE else None
        fields = [
            "id",
            "tran_id",
            "val_id",
            "bank_tran_id",
            "amount",
            "currency",
            "status",
            "product_name",
            "product_category",
            "customer_name",
            "customer_email",
            "customer_phone",
            "created_at",
            "updated_at",
            "payment_completed_at",
            "is_validated",
        ]
        read_only_fields = [
            "id",
            "val_id",
            "bank_tran_id",
            "status",
            "created_at",
            "updated_at",
            "payment_completed_at",
            "is_validated",
        ]


class PaymentInitiationSerializer(serializers.Serializer):
    """Serializer for payment initiation data."""

    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=10, default="BDT")
    tran_id = serializers.CharField(max_length=100)

    # Product information
    product_name = serializers.CharField(max_length=255, required=False)
    product_category = serializers.CharField(max_length=100, required=False)
    product_profile = serializers.CharField(max_length=100, default="general")

    # Customer information
    cus_name = serializers.CharField(max_length=255)
    cus_email = serializers.EmailField()
    cus_phone = serializers.CharField(max_length=20)
    cus_add1 = serializers.CharField(max_length=255, required=False)
    cus_add2 = serializers.CharField(max_length=255, required=False)
    cus_city = serializers.CharField(max_length=100, required=False)
    cus_state = serializers.CharField(max_length=100, required=False)
    cus_postcode = serializers.CharField(max_length=20, required=False)
    cus_country = serializers.CharField(max_length=100, default="Bangladesh")

    # Shipping information (optional)
    ship_name = serializers.CharField(max_length=255, required=False)
    ship_add1 = serializers.CharField(max_length=255, required=False)
    ship_add2 = serializers.CharField(max_length=255, required=False)
    ship_city = serializers.CharField(max_length=100, required=False)
    ship_state = serializers.CharField(max_length=100, required=False)
    ship_postcode = serializers.CharField(max_length=20, required=False)
    ship_country = serializers.CharField(max_length=100, required=False)

    # URLs (optional - will use default from settings if not provided)
    success_url = serializers.URLField(required=False)
    fail_url = serializers.URLField(required=False)
    cancel_url = serializers.URLField(required=False)
    ipn_url = serializers.URLField(required=False)

    # Additional fields
    value_a = serializers.CharField(max_length=255, required=False)
    value_b = serializers.CharField(max_length=255, required=False)
    value_c = serializers.CharField(max_length=255, required=False)
    value_d = serializers.CharField(max_length=255, required=False)


class RefundSerializer(serializers.Serializer):
    """Serializer for refund requests."""

    bank_tran_id = serializers.CharField(max_length=100)
    refund_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    refund_remarks = serializers.CharField(max_length=500)
    refe_id = serializers.CharField(max_length=100, required=False)


if DRF_AVAILABLE:

    class TransactionViewSet(viewsets.ModelViewSet):
        """ViewSet for managing transactions."""

        queryset = Transaction.objects.all()
        serializer_class = TransactionSerializer
        permission_classes = [IsAuthenticated]
        lookup_field = "tran_id"

        def get_queryset(self):
            """Filter transactions by authenticated user if user field exists."""
            queryset = super().get_queryset()
            if hasattr(self.request, "user") and self.request.user.is_authenticated:
                # Only show user's own transactions unless user is staff
                if not self.request.user.is_staff:
                    queryset = queryset.filter(user=self.request.user)
            return queryset

        @action(detail=True, methods=["post"])
        def validate_transaction(self, request, tran_id=None):
            """Validate a specific transaction."""
            transaction = self.get_object()

            try:
                client = SSLCommerzClient()
                validation_result = client.validate_transaction(
                    transaction.val_id or transaction.tran_id, str(transaction.amount)
                )

                # Update transaction status if validation is successful
                if validation_result.get("status") == "VALID":
                    transaction.is_validated = True
                    transaction.status = "VALIDATED"
                    transaction.save()

                return Response(
                    {
                        "status": "success",
                        "validation_result": validation_result,
                        "transaction_updated": validation_result.get("status")
                        == "VALID",
                    }
                )

            except SSLCommerzError as e:
                return Response(
                    {"status": "error", "message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    class PaymentViewSet(viewsets.ViewSet):
        """ViewSet for payment operations."""

        permission_classes = [IsAuthenticated]

        @action(detail=False, methods=["post"])
        def initiate(self, request):
            """Initiate a new payment."""
            serializer = PaymentInitiationSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    client = SSLCommerzClient()

                    # Create transaction record
                    transaction_data = serializer.validated_data
                    transaction = Transaction.objects.create(
                        tran_id=transaction_data["tran_id"],
                        amount=transaction_data["total_amount"],
                        currency=transaction_data["currency"],
                        customer_name=transaction_data["cus_name"],
                        customer_email=transaction_data["cus_email"],
                        customer_phone=transaction_data["cus_phone"],
                        product_name=transaction_data.get("product_name", ""),
                        product_category=transaction_data.get("product_category", ""),
                        user=request.user if hasattr(request, "user") else None,
                        status="PENDING",
                    )

                    # Initiate payment with SSLCOMMERZ
                    response = client.initiate_payment(transaction_data)

                    # Update transaction with gateway response
                    transaction.gateway_response = response
                    transaction.save()

                    return Response(
                        {
                            "status": "success",
                            "transaction_id": transaction.tran_id,
                            "gateway_url": response.get("GatewayPageURL"),
                            "gateway_response": response,
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

        @action(detail=False, methods=["post"])
        def handle_ipn(self, request):
            """Handle IPN callback."""
            try:
                result = handle_ipn(dict(request.data))

                # Update transaction if exists
                try:
                    transaction = Transaction.objects.get(tran_id=result["tran_id"])
                    transaction.update_from_ipn(result["ipn_data"])

                    if result["valid"]:
                        transaction.mark_as_successful()
                    else:
                        transaction.mark_as_failed("IPN validation failed")

                except Transaction.DoesNotExist:
                    logger.warning(f"Transaction {result['tran_id']} not found")

                return Response(
                    {
                        "status": "success",
                        "message": "IPN processed successfully",
                        "result": result,
                    }
                )

            except SSLCommerzError as e:
                return Response(
                    {"status": "error", "message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        @action(detail=False, methods=["post"])
        def refund(self, request):
            """Process a refund."""
            serializer = RefundSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    client = SSLCommerzClient()
                    refund_result = client.process_refund(serializer.validated_data)

                    return Response(
                        {"status": "success", "refund_result": refund_result}
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

else:
    # Dummy classes when DRF is not available
    class TransactionViewSet:
        pass

    class PaymentViewSet:
        pass
