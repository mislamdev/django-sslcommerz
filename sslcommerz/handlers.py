"""
IPN (Instant Payment Notification) handling for SSLCOMMERZ.
"""
import logging
from typing import Dict, Any

from django.http import HttpRequest

from .client import SSLCommerzClient
from .config import get_config
from .exceptions import SSLCommerzIPNError
from .signals import payment_successful, payment_failed, ipn_received

logger = logging.getLogger(__name__)


class IPNHandler:
    """
    Handle SSLCOMMERZ IPN (Instant Payment Notification) requests.
    """

    def __init__(self, config=None):
        """
        Initialize IPN handler.

        Args:
            config: Optional custom configuration
        """
        self.config = config or get_config()
        self.client = SSLCommerzClient(config)

    def process_ipn(self, ipn_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an IPN request from SSLCOMMERZ.

        Args:
            ipn_data: IPN data from SSLCOMMERZ

        Returns:
            Dictionary containing processing result

        Raises:
            SSLCommerzIPNError: If IPN processing fails
        """
        try:
            # Extract essential data
            tran_id = ipn_data.get("tran_id")
            val_id = ipn_data.get("val_id")
            amount = ipn_data.get("amount")
            status = ipn_data.get("status")

            if not all([tran_id, val_id, amount]):
                raise SSLCommerzIPNError("Missing required IPN fields")

            # Log IPN received
            logger.info(f"IPN received for transaction: {tran_id}")

            # Send signal for IPN received
            ipn_received.send(
                sender=self.__class__, ipn_data=ipn_data, tran_id=tran_id, status=status
            )

            # Validate transaction if auto-validation is enabled
            is_valid = True
            validation_result = None

            if self.config.get("AUTO_VALIDATE_IPN", True):
                try:
                    validation_result = self.client.validate_transaction(val_id, amount)
                    is_valid = validation_result.get(
                        "status"
                    ) == "VALID" and not validation_result.get("amount_mismatch", False)
                except Exception as e:
                    logger.error(f"Transaction validation failed: {e}")
                    is_valid = False

            result = {
                "valid": is_valid,
                "tran_id": tran_id,
                "val_id": val_id,
                "amount": amount,
                "status": status,
                "ipn_data": ipn_data,
                "validation_result": validation_result,
            }

            # Send appropriate signals based on status and validation
            if is_valid and status in ["VALID", "VALIDATED"]:
                payment_successful.send(
                    sender=self.__class__,
                    tran_id=tran_id,
                    amount=amount,
                    ipn_data=ipn_data,
                    validation_result=validation_result,
                )
                logger.info(f"Payment successful for transaction: {tran_id}")
            else:
                payment_failed.send(
                    sender=self.__class__,
                    tran_id=tran_id,
                    amount=amount,
                    ipn_data=ipn_data,
                    reason=f"Status: {status}, Valid: {is_valid}",
                )
                logger.warning(f"Payment failed for transaction: {tran_id}")

            return result

        except Exception as e:
            logger.error(f"IPN processing failed: {e}")
            raise SSLCommerzIPNError(f"IPN processing failed: {str(e)}")

    def verify_hash(self, ipn_data: Dict[str, Any]) -> bool:
        """
        Verify the hash signature of IPN data (if provided by SSLCOMMERZ).

        Args:
            ipn_data: IPN data to verify

        Returns:
            True if hash is valid, False otherwise
        """
        # Note: This is a placeholder for hash verification
        # SSLCOMMERZ v4 may not always include hash verification
        # Implementation would depend on specific hash algorithm used

        verify_sign = ipn_data.get("verify_sign")
        if not verify_sign:
            # No signature to verify
            return True

        # Implement hash verification logic here if needed
        # This would typically involve creating a hash from the data
        # and comparing it with the provided signature

        return True


def handle_ipn(ipn_data: Dict[str, Any], config=None) -> Dict[str, Any]:
    """
    Convenience function to handle IPN data.

    Args:
        ipn_data: IPN data from SSLCOMMERZ
        config: Optional custom configuration

    Returns:
        Dictionary containing processing result
    """
    handler = IPNHandler(config)
    return handler.process_ipn(ipn_data)


def handle_ipn_from_request(request: HttpRequest, config=None) -> Dict[str, Any]:
    """
    Handle IPN from Django HttpRequest.

    Args:
        request: Django HttpRequest object
        config: Optional custom configuration

    Returns:
        Dictionary containing processing result
    """
    if request.method != "POST":
        raise SSLCommerzIPNError("IPN must be POST request")

    # Convert QueryDict to regular dict
    ipn_data = dict(request.POST.items())

    return handle_ipn(ipn_data, config)
