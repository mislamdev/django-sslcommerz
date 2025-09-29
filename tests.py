"""
Test suite for SSLCOMMERZ package.
"""
import json
from decimal import Decimal
from unittest.mock import patch, Mock

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from sslcommerz.client import SSLCommerzClient
from sslcommerz.config import SSLCommerzConfig, validate_config
from sslcommerz.handlers import IPNHandler, handle_ipn
from sslcommerz.models import Transaction, RefundTransaction
from sslcommerz.utils import (
    generate_transaction_id,
    validate_amount,
    validate_currency,
    validate_phone_number,
    sanitize_customer_data,
)
from sslcommerz.exceptions import (
    SSLCommerzError,
    SSLCommerzAPIError,
    SSLCommerzValidationError,
    SSLCommerzIPNError,
)


User = get_user_model()


class SSLCommerzConfigTest(TestCase):
    """Test SSLCOMMERZ configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SSLCommerzConfig()
        self.assertTrue(config.is_sandbox)
        self.assertEqual(config.get("TIMEOUT"), 30)
        self.assertTrue(config.get("VERIFY_SSL"))

    @override_settings(
        SSLCOMMERZ={
            "STORE_ID": "test_store",
            "STORE_PASSWORD": "test_password",
            "IS_SANDBOX": False,
        }
    )
    def test_django_settings_config(self):
        """Test configuration from Django settings."""
        config = SSLCommerzConfig()
        self.assertEqual(config.store_id, "test_store")
        self.assertEqual(config.store_password, "test_password")
        self.assertFalse(config.is_sandbox)

    def test_sandbox_urls(self):
        """Test sandbox URL generation."""
        config = SSLCommerzConfig()
        config._config["IS_SANDBOX"] = True
        self.assertIn("sandbox", config.base_url)
        self.assertIn("sandbox", config.session_url)

    def test_production_urls(self):
        """Test production URL generation."""
        config = SSLCommerzConfig()
        config._config["IS_SANDBOX"] = False
        self.assertNotIn("sandbox", config.base_url)
        self.assertIn("securepay", config.base_url)


class SSLCommerzClientTest(TestCase):
    """Test SSLCOMMERZ client."""

    def setUp(self):
        self.client = SSLCommerzClient()
        self.sample_payment_data = {
            "total_amount": 100.00,
            "currency": "BDT",
            "tran_id": "TEST_123456",
            "product_name": "Test Product",
            "product_category": "goods",
            "product_profile": "general",
            "cus_name": "John Doe",
            "cus_email": "john@example.com",
            "cus_phone": "01700000000",
            "cus_add1": "Test Address",
            "cus_city": "Dhaka",
            "cus_country": "Bangladesh",
        }

    def test_validate_payment_data_success(self):
        """Test successful payment data validation."""
        # Should not raise any exception
        self.client._validate_payment_data(self.sample_payment_data)

    def test_validate_payment_data_missing_fields(self):
        """Test payment data validation with missing fields."""
        incomplete_data = {
            "total_amount": 100.00,
            "currency": "BDT"
            # Missing required fields
        }

        with self.assertRaises(SSLCommerzValidationError):
            self.client._validate_payment_data(incomplete_data)

    def test_validate_payment_data_invalid_amount(self):
        """Test payment data validation with invalid amount."""
        invalid_data = self.sample_payment_data.copy()
        invalid_data["total_amount"] = -100

        with self.assertRaises(SSLCommerzValidationError):
            self.client._validate_payment_data(invalid_data)

    def test_validate_payment_data_invalid_currency(self):
        """Test payment data validation with invalid currency."""
        invalid_data = self.sample_payment_data.copy()
        invalid_data["currency"] = "INVALID"

        with self.assertRaises(SSLCommerzValidationError):
            self.client._validate_payment_data(invalid_data)

    @patch("requests.Session.post")
    def test_initiate_payment_success(self, mock_post):
        """Test successful payment initiation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "GatewayPageURL": "https://sandbox.sslcommerz.com/EasyCheckOut/testkey123",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.initiate_payment(self.sample_payment_data)

        self.assertEqual(result["status"], "SUCCESS")
        self.assertIn("GatewayPageURL", result)

    @patch("requests.Session.post")
    def test_initiate_payment_api_error(self, mock_post):
        """Test payment initiation with API error."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "FAILED",
            "failedreason": "Invalid store credentials",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with self.assertRaises(SSLCommerzAPIError):
            self.client.initiate_payment(self.sample_payment_data)


class IPNHandlerTest(TestCase):
    """Test IPN handling."""

    def setUp(self):
        self.handler = IPNHandler()
        self.sample_ipn_data = {
            "tran_id": "TEST_123456",
            "val_id": "VAL_123456",
            "amount": "100.00",
            "status": "VALID",
            "currency": "BDT",
            "bank_tran_id": "BANK_123456",
            "card_type": "VISA",
        }

    def test_process_ipn_missing_fields(self):
        """Test IPN processing with missing required fields."""
        incomplete_data = {
            "tran_id": "TEST_123456"
            # Missing required fields
        }

        with self.assertRaises(SSLCommerzIPNError):
            self.handler.process_ipn(incomplete_data)

    @patch("sslcommerz.handlers.SSLCommerzClient.validate_transaction")
    def test_process_ipn_success(self, mock_validate):
        """Test successful IPN processing."""
        mock_validate.return_value = {"status": "VALID", "amount": "100.00"}

        result = self.handler.process_ipn(self.sample_ipn_data)

        self.assertTrue(result["valid"])
        self.assertEqual(result["tran_id"], "TEST_123456")
        self.assertEqual(result["status"], "VALID")


class TransactionModelTest(TestCase):
    """Test Transaction model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.transaction = Transaction.objects.create(
            tran_id="TEST_123456",
            amount=Decimal("100.00"),
            currency="BDT",
            customer_name="John Doe",
            customer_email="john@example.com",
            customer_phone="01700000000",
            user=self.user,
        )

    def test_transaction_creation(self):
        """Test transaction creation."""
        self.assertEqual(self.transaction.tran_id, "TEST_123456")
        self.assertEqual(self.transaction.amount, Decimal("100.00"))
        self.assertEqual(self.transaction.status, "PENDING")
        self.assertFalse(self.transaction.is_validated)

    def test_mark_as_successful(self):
        """Test marking transaction as successful."""
        self.transaction.mark_as_successful()
        self.assertEqual(self.transaction.status, "VALID")
        self.assertIsNotNone(self.transaction.payment_completed_at)

    def test_mark_as_failed(self):
        """Test marking transaction as failed."""
        self.transaction.mark_as_failed("Test failure reason")
        self.assertEqual(self.transaction.status, "FAILED")
        self.assertEqual(
            self.transaction.metadata["failure_reason"], "Test failure reason"
        )

    def test_update_from_ipn(self):
        """Test updating transaction from IPN data."""
        ipn_data = {
            "val_id": "VAL_123456",
            "bank_tran_id": "BANK_123456",
            "status": "VALID",
        }

        self.transaction.update_from_ipn(ipn_data)
        self.assertEqual(self.transaction.val_id, "VAL_123456")
        self.assertEqual(self.transaction.bank_tran_id, "BANK_123456")
        self.assertEqual(self.transaction.status, "VALID")

    def test_transaction_properties(self):
        """Test transaction properties."""
        # Test is_pending
        self.assertTrue(self.transaction.is_pending)

        # Test is_successful after marking as successful
        self.transaction.mark_as_successful()
        self.assertTrue(self.transaction.is_successful)

        # Test can_be_refunded
        self.assertTrue(self.transaction.can_be_refunded)


class UtilsTest(TestCase):
    """Test utility functions."""

    def test_generate_transaction_id(self):
        """Test transaction ID generation."""
        tran_id = generate_transaction_id()
        self.assertTrue(tran_id.startswith("TXN_"))
        self.assertGreater(len(tran_id), 15)

        # Test with custom prefix
        custom_id = generate_transaction_id("CUSTOM")
        self.assertTrue(custom_id.startswith("CUSTOM_"))

    def test_validate_amount(self):
        """Test amount validation."""
        # Valid amounts
        self.assertEqual(validate_amount(100), 100.0)
        self.assertEqual(validate_amount("150.50"), 150.5)

        # Invalid amounts
        with self.assertRaises(ValidationError):
            validate_amount(-100)

        with self.assertRaises(ValidationError):
            validate_amount("invalid")

    def test_validate_currency(self):
        """Test currency validation."""
        # Valid currencies
        self.assertEqual(validate_currency("bdt"), "BDT")
        self.assertEqual(validate_currency("USD"), "USD")

        # Invalid currency
        with self.assertRaises(ValidationError):
            validate_currency("INVALID")

    def test_validate_phone_number(self):
        """Test phone number validation."""
        # Valid phone numbers
        self.assertEqual(validate_phone_number("01700000000"), "01700000000")
        self.assertEqual(validate_phone_number("880 1700000000"), "01700000000")
        self.assertEqual(validate_phone_number("+880 17-0000-0000"), "01700000000")

        # Invalid phone numbers
        with self.assertRaises(ValidationError):
            validate_phone_number("123456")  # Too short

        with self.assertRaises(ValidationError):
            validate_phone_number("01200000000")  # Invalid prefix

    def test_sanitize_customer_data(self):
        """Test customer data sanitization."""
        raw_data = {
            "cus_name": "John & Jane Doe <script>",
            "cus_email": "JOHN@EXAMPLE.COM",
            "cus_phone": "+880 17-0000-0000",
            "total_amount": "100.50",
            "invalid_field": "should be ignored",
        }

        sanitized = sanitize_customer_data(raw_data)

        self.assertEqual(sanitized["cus_name"], "John and Jane Doe")
        self.assertEqual(sanitized["cus_email"], "john@example.com")
        self.assertEqual(sanitized["cus_phone"], "01700000000")
        self.assertEqual(sanitized["total_amount"], 100.5)
        self.assertNotIn("invalid_field", sanitized)
