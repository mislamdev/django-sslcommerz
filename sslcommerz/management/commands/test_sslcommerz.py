"""
Django management command to test SSLCOMMERZ configuration.
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from sslcommerz.client import SSLCommerzClient
from sslcommerz.config import get_config, validate_config
from sslcommerz.exceptions import SSLCommerzError
from sslcommerz.utils import get_environment_info


class Command(BaseCommand):
    help = "Test SSLCOMMERZ configuration and connectivity"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test-payment",
            action="store_true",
            help="Test payment initiation (sandbox only)",
        )
        parser.add_argument(
            "--validate-transaction",
            type=str,
            help="Validate a specific transaction ID",
        )
        parser.add_argument(
            "--amount",
            type=float,
            default=10.0,
            help="Amount to use for test payment (default: 10.0)",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("SSLCOMMERZ Configuration Test"))
        self.stdout.write("=" * 50)

        # Test configuration
        try:
            validate_config()
            self.stdout.write(self.style.SUCCESS("✓ Configuration validation passed"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Configuration validation failed: {e}")
            )
            return

        # Show environment info
        config = get_config()
        env_info = get_environment_info()

        self.stdout.write("\nEnvironment Information:")
        self.stdout.write(f"  Mode: {'Sandbox' if config.is_sandbox else 'Production'}")
        self.stdout.write(f"  Store ID: {config.store_id}")
        self.stdout.write(f"  Base URL: {config.base_url}")
        self.stdout.write(f"  Production Ready: {env_info['production_ready']}")

        self.stdout.write("\nConfigured URLs:")
        for url_type, configured in env_info["configured_urls"].items():
            status = "✓" if configured else "✗"
            self.stdout.write(f"  {url_type.title()}: {status}")

        # Test connectivity
        self.stdout.write("\nTesting API Connectivity...")
        try:
            client = SSLCommerzClient()
            # Test with a minimal request to check connectivity
            self.stdout.write(
                self.style.SUCCESS("✓ API client initialized successfully")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ API client initialization failed: {e}")
            )
            return

        # Test payment initiation if requested
        if options["test_payment"]:
            if not config.is_sandbox:
                self.stdout.write(
                    self.style.ERROR("✗ Test payment only available in sandbox mode")
                )
                return

            self._test_payment_initiation(client, options["amount"])

        # Test transaction validation if requested
        if options["validate_transaction"]:
            self._test_transaction_validation(client, options["validate_transaction"])

        self.stdout.write(self.style.SUCCESS("\nConfiguration test completed!"))

    def _test_payment_initiation(self, client, amount):
        """Test payment initiation."""
        self.stdout.write("\nTesting Payment Initiation...")

        test_data = {
            "total_amount": amount,
            "currency": "BDT",
            "tran_id": f'TEST_{timezone.now().strftime("%Y%m%d%H%M%S")}',
            "product_name": "Test Product",
            "product_category": "testing",
            "product_profile": "general",
            "cus_name": "Test Customer",
            "cus_email": "test@example.com",
            "cus_phone": "01700000000",
            "cus_add1": "Test Address",
            "cus_city": "Dhaka",
            "cus_country": "Bangladesh",
        }

        try:
            response = client.initiate_payment(test_data)

            if response.get("status") == "SUCCESS":
                self.stdout.write(self.style.SUCCESS("✓ Payment initiation successful"))
                self.stdout.write(f"  Transaction ID: {test_data['tran_id']}")
                self.stdout.write(
                    f"  Gateway URL: {response.get('GatewayPageURL', 'N/A')}"
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠ Payment initiation returned: {response.get('status')}"
                    )
                )

        except SSLCommerzError as e:
            self.stdout.write(self.style.ERROR(f"✗ Payment initiation failed: {e}"))

    def _test_transaction_validation(self, client, tran_id):
        """Test transaction validation."""
        self.stdout.write(f"\nTesting Transaction Validation for: {tran_id}")

        try:
            # Try to get amount from database first
            try:
                from sslcommerz.models import Transaction

                transaction = Transaction.objects.get(tran_id=tran_id)
                amount = str(transaction.amount)
                self.stdout.write(
                    f"  Found transaction in database: {amount} {transaction.currency}"
                )
            except:
                amount = "10.00"  # Default amount
                self.stdout.write(f"  Using default amount: {amount}")

            result = client.validate_transaction(tran_id, amount)

            self.stdout.write(f"  Status: {result.get('status', 'Unknown')}")
            self.stdout.write(f"  Amount: {result.get('amount', 'N/A')}")
            self.stdout.write(f"  Currency: {result.get('currency', 'N/A')}")

            if result.get("status") == "VALID":
                self.stdout.write(
                    self.style.SUCCESS("✓ Transaction validation successful")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Transaction status: {result.get('status')}")
                )

        except SSLCommerzError as e:
            self.stdout.write(self.style.ERROR(f"✗ Transaction validation failed: {e}"))
