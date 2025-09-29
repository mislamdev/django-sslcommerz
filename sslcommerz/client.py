"""
SSLCOMMERZ API client for handling payment gateway operations.
"""
import json
import logging
from typing import Dict, Any, Union

import requests
from django.core.exceptions import ValidationError

from .config import get_config
from .exceptions import SSLCommerzAPIError, SSLCommerzValidationError

logger = logging.getLogger(__name__)


class SSLCommerzClient:
    """
    Main client for interacting with SSLCOMMERZ API v4.
    """

    def __init__(self, config=None):
        """
        Initialize SSLCOMMERZ client.

        Args:
            config: Optional custom configuration. Uses global config if None.
        """
        self.config = config or get_config()
        self._session = requests.Session()

        # Set default timeout and SSL verification
        self._session.timeout = self.config.get("TIMEOUT", 30)
        self._session.verify = self.config.get("VERIFY_SSL", True)

    def initiate_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a payment session with SSLCOMMERZ.

        Args:
            payment_data: Dictionary containing payment information

        Returns:
            Dictionary containing API response

        Raises:
            SSLCommerzAPIError: If API request fails
            SSLCommerzValidationError: If payment data is invalid
        """
        # Validate required fields
        self._validate_payment_data(payment_data)

        # Prepare request data
        request_data = self._prepare_payment_data(payment_data)

        # Log request if enabled
        if self.config.get("LOG_REQUESTS", False):
            logger.info(f"Initiating payment: {json.dumps(request_data, default=str)}")

        try:
            response = self._session.post(
                self.config.session_url,
                data=request_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()

            result = response.json()

            if self.config.get("LOG_REQUESTS", False):
                logger.info(f"Payment initiation response: {json.dumps(result)}")

            if result.get("status") != "SUCCESS":
                raise SSLCommerzAPIError(
                    f"Payment initiation failed: {result.get('failedreason', 'Unknown error')}"
                )

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Payment initiation request failed: {e}")
            raise SSLCommerzAPIError(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise SSLCommerzAPIError("Invalid API response format")

    def validate_transaction(
        self, tran_id: str, amount: Union[str, float]
    ) -> Dict[str, Any]:
        """
        Validate a transaction with SSLCOMMERZ.

        Args:
            tran_id: Transaction ID to validate
            amount: Transaction amount to validate

        Returns:
            Dictionary containing validation result

        Raises:
            SSLCommerzAPIError: If API request fails
        """
        validation_data = {
            "store_id": self.config.store_id,
            "store_passwd": self.config.store_password,
            "val_id": tran_id,
            "format": "json",
        }

        try:
            response = self._session.get(
                self.config.validation_url, params=validation_data
            )
            response.raise_for_status()

            result = response.json()

            if self.config.get("LOG_REQUESTS", False):
                logger.info(f"Transaction validation response: {json.dumps(result)}")

            # Validate amount if transaction is valid
            if result.get("status") == "VALID":
                response_amount = float(result.get("amount", 0))
                expected_amount = float(amount)

                if (
                    abs(response_amount - expected_amount) > 0.01
                ):  # Allow 1 paisa difference
                    logger.warning(
                        f"Amount mismatch for transaction {tran_id}: "
                        f"expected {expected_amount}, got {response_amount}"
                    )
                    result["amount_mismatch"] = True
                else:
                    result["amount_mismatch"] = False

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Transaction validation request failed: {e}")
            raise SSLCommerzAPIError(f"Validation API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise SSLCommerzAPIError("Invalid validation API response format")

    def process_refund(self, refund_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a refund request.

        Args:
            refund_data: Dictionary containing refund information

        Returns:
            Dictionary containing refund result

        Raises:
            SSLCommerzAPIError: If API request fails
            SSLCommerzValidationError: If refund data is invalid
        """
        # Validate required refund fields
        required_fields = ["bank_tran_id", "refund_amount", "refund_remarks"]
        missing_fields = [
            field for field in required_fields if not refund_data.get(field)
        ]

        if missing_fields:
            raise SSLCommerzValidationError(
                f"Missing required refund fields: {', '.join(missing_fields)}"
            )

        request_data = {
            "store_id": self.config.store_id,
            "store_passwd": self.config.store_password,
            "refund_amount": refund_data["refund_amount"],
            "refund_remarks": refund_data["refund_remarks"],
            "bank_tran_id": refund_data["bank_tran_id"],
            "refe_id": refund_data.get("refe_id", ""),
            "format": "json",
        }

        try:
            response = self._session.post(self.config.refund_url, data=request_data)
            response.raise_for_status()

            result = response.json()

            if self.config.get("LOG_REQUESTS", False):
                logger.info(f"Refund response: {json.dumps(result)}")

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Refund request failed: {e}")
            raise SSLCommerzAPIError(f"Refund API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise SSLCommerzAPIError("Invalid refund API response format")

    def _validate_payment_data(self, payment_data: Dict[str, Any]) -> None:
        """
        Validate payment data before sending to API.

        Args:
            payment_data: Payment data to validate

        Raises:
            SSLCommerzValidationError: If validation fails
        """
        required_fields = [
            "total_amount",
            "currency",
            "tran_id",
            "cus_name",
            "cus_email",
            "cus_phone",
        ]

        missing_fields = [
            field for field in required_fields if not payment_data.get(field)
        ]

        if missing_fields:
            raise SSLCommerzValidationError(
                f"Missing required payment fields: {', '.join(missing_fields)}"
            )

        # Validate amount
        try:
            amount = float(payment_data["total_amount"])
            if amount <= 0:
                raise SSLCommerzValidationError("Amount must be greater than 0")
        except (ValueError, TypeError):
            raise SSLCommerzValidationError("Invalid amount format")

        # Validate currency
        valid_currencies = ["BDT", "USD", "EUR", "GBP", "JPY"]
        if payment_data["currency"] not in valid_currencies:
            raise SSLCommerzValidationError(
                f"Invalid currency. Supported currencies: {', '.join(valid_currencies)}"
            )

        # Validate email format (basic validation)
        email = payment_data["cus_email"]
        if "@" not in email or "." not in email.split("@")[-1]:
            raise SSLCommerzValidationError("Invalid email format")

    def _prepare_payment_data(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare payment data for API request.

        Args:
            payment_data: Raw payment data

        Returns:
            Formatted payment data for API
        """
        # Base required data
        request_data = {
            "store_id": self.config.store_id,
            "store_passwd": self.config.store_password,
            "total_amount": payment_data["total_amount"],
            "currency": payment_data["currency"],
            "tran_id": payment_data["tran_id"],
            "success_url": payment_data.get("success_url")
            or self.config.get("SUCCESS_URL", ""),
            "fail_url": payment_data.get("fail_url") or self.config.get("FAIL_URL", ""),
            "cancel_url": payment_data.get("cancel_url")
            or self.config.get("CANCEL_URL", ""),
            "ipn_url": payment_data.get("ipn_url") or self.config.get("IPN_URL", ""),
        }

        # Customer information
        customer_fields = [
            "cus_name",
            "cus_email",
            "cus_add1",
            "cus_add2",
            "cus_city",
            "cus_state",
            "cus_postcode",
            "cus_country",
            "cus_phone",
            "cus_fax",
        ]

        for field in customer_fields:
            if field in payment_data:
                request_data[field] = payment_data[field]

        # Product information
        product_fields = [
            "product_name",
            "product_category",
            "product_profile",
            "product_amount",
            "vat",
            "discount_amount",
            "convenience_fee",
        ]

        for field in product_fields:
            if field in payment_data:
                request_data[field] = payment_data[field]

        # Shipping information
        shipping_fields = [
            "ship_name",
            "ship_add1",
            "ship_add2",
            "ship_city",
            "ship_state",
            "ship_postcode",
            "ship_country",
        ]

        for field in shipping_fields:
            if field in payment_data:
                request_data[field] = payment_data[field]

        # Additional fields
        additional_fields = [
            "value_a",
            "value_b",
            "value_c",
            "value_d",
            "multi_card_name",
            "allowed_bin",
            "emi_option",
        ]

        for field in additional_fields:
            if field in payment_data:
                request_data[field] = payment_data[field]

        return request_data
