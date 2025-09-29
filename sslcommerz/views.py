"""
Django views for SSLCOMMERZ integration.
"""
import logging

from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import View

from .exceptions import SSLCommerzIPNError
from .handlers import handle_ipn_from_request
from .models import Transaction

logger = logging.getLogger(__name__)


class BaseIPNView(View):
    """
    Base view for handling SSLCOMMERZ IPN callbacks.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle IPN POST request."""
        try:
            result = handle_ipn_from_request(request)

            # Try to update transaction model if it exists
            try:
                transaction = Transaction.objects.get(tran_id=result["tran_id"])
                transaction.update_from_ipn(result["ipn_data"])

                if result["valid"] and result["status"] in ["VALID", "VALIDATED"]:
                    transaction.mark_as_successful()
                elif not result["valid"]:
                    transaction.mark_as_failed("IPN validation failed")

            except Transaction.DoesNotExist:
                logger.warning(f"Transaction {result['tran_id']} not found in database")

            # Call custom handler if implemented
            self.handle_ipn_success(result)

            return self.success_response(result)

        except SSLCommerzIPNError as e:
            logger.error(f"IPN processing failed: {e}")
            self.handle_ipn_error(str(e))
            return self.error_response(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in IPN processing: {e}")
            self.handle_ipn_error(str(e))
            return self.error_response("Internal server error")

    def handle_ipn_success(self, result):
        """
        Override this method to implement custom IPN success handling.

        Args:
            result: Dictionary containing IPN processing result
        """
        pass

    def handle_ipn_error(self, error_message):
        """
        Override this method to implement custom IPN error handling.

        Args:
            error_message: Error message string
        """
        pass

    def success_response(self, result):
        """Return success response."""
        return HttpResponse("OK", status=200)

    def error_response(self, error_message):
        """Return error response."""
        return HttpResponse("ERROR", status=400)


class IPNView(BaseIPNView):
    """
    Default IPN view that returns simple HTTP responses.
    """

    pass


class IPNJsonView(BaseIPNView):
    """
    IPN view that returns JSON responses.
    """

    def success_response(self, result):
        """Return JSON success response."""
        return JsonResponse(
            {
                "status": "success",
                "message": "IPN processed successfully",
                "tran_id": result["tran_id"],
            }
        )

    def error_response(self, error_message):
        """Return JSON error response."""
        return JsonResponse({"status": "error", "message": error_message}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def simple_ipn_view(request):
    """
    Simple function-based IPN view.
    """
    try:
        result = handle_ipn_from_request(request)
        logger.info(f"IPN processed successfully for transaction: {result['tran_id']}")
        return HttpResponse("OK")
    except Exception as e:
        logger.error(f"IPN processing failed: {e}")
        return HttpResponse("ERROR", status=400)


class TransactionStatusView(View):
    """
    View to check transaction status.
    """

    def get(self, request, tran_id):
        """Get transaction status."""
        try:
            transaction = get_object_or_404(Transaction, tran_id=tran_id)

            return JsonResponse(
                {
                    "tran_id": transaction.tran_id,
                    "status": transaction.status,
                    "amount": str(transaction.amount),
                    "currency": transaction.currency,
                    "is_successful": transaction.is_successful,
                    "created_at": transaction.created_at.isoformat(),
                    "updated_at": transaction.updated_at.isoformat(),
                }
            )

        except Http404:
            return JsonResponse({"error": "Transaction not found"}, status=404)
