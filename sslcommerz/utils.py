"""
Utility functions for SSLCOMMERZ package.
"""
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any

from django.core.exceptions import ValidationError
from django.utils import timezone

from .config import get_config


def generate_transaction_id(prefix: str = "TXN") -> str:
    """
    Generate a unique transaction ID.

    Args:
        prefix: Prefix for the transaction ID

    Returns:
        Unique transaction ID string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"{prefix}_{timestamp}_{unique_id}"


def validate_amount(amount: Any) -> float:
    """
    Validate and convert amount to float.

    Args:
        amount: Amount to validate

    Returns:
        Validated amount as float

    Raises:
        ValidationError: If amount is invalid
    """
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            raise ValidationError("Amount must be greater than 0")
        return amount_float
    except (ValueError, TypeError):
        raise ValidationError("Invalid amount format")


def validate_currency(currency: str) -> str:
    """
    Validate currency code.

    Args:
        currency: Currency code to validate

    Returns:
        Validated currency code

    Raises:
        ValidationError: If currency is invalid
    """
    valid_currencies = ["BDT", "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "SGD"]

    if currency.upper() not in valid_currencies:
        raise ValidationError(
            f"Invalid currency. Supported currencies: {', '.join(valid_currencies)}"
        )

    return currency.upper()


def validate_phone_number(phone: str) -> str:
    """
    Validate Bangladeshi phone number.

    Args:
        phone: Phone number to validate

    Returns:
        Validated phone number

    Raises:
        ValidationError: If phone number is invalid
    """
    # Remove spaces and dashes
    phone = phone.replace(" ", "").replace("-", "")

    # Check if it's a valid Bangladeshi number
    if phone.startswith("+880"):
        phone = phone[4:]
    elif phone.startswith("880"):
        phone = phone[3:]
    elif phone.startswith("0"):
        phone = phone[1:]

    # Should be 10 digits for Bangladeshi mobile numbers
    if not phone.isdigit() or len(phone) != 10:
        raise ValidationError("Invalid phone number format")

    # Check if it starts with valid mobile prefixes
    valid_prefixes = ["13", "14", "15", "16", "17", "18", "19"]
    if phone[:2] not in valid_prefixes:
        raise ValidationError("Invalid mobile number prefix")

    return f"0{phone}"


def sanitize_customer_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize customer data for SSLCOMMERZ API.

    Args:
        data: Customer data dictionary

    Returns:
        Sanitized customer data
    """
    sanitized = {}

    # String fields that need sanitization
    string_fields = [
        "cus_name",
        "cus_add1",
        "cus_add2",
        "cus_city",
        "cus_state",
        "ship_name",
        "ship_add1",
        "ship_add2",
        "ship_city",
        "ship_state",
        "product_name",
        "product_category",
    ]

    for field in string_fields:
        if field in data and data[field]:
            # Remove special characters that might cause issues
            value = str(data[field]).strip()
            # Replace problematic characters
            value = value.replace("&", "and").replace("<", "").replace(">", "")
            sanitized[field] = value[:100]  # Limit length

    # Email field
    if "cus_email" in data:
        sanitized["cus_email"] = str(data["cus_email"]).strip().lower()

    # Phone field
    if "cus_phone" in data:
        try:
            sanitized["cus_phone"] = validate_phone_number(data["cus_phone"])
        except ValidationError:
            sanitized["cus_phone"] = str(data["cus_phone"])[:20]

    # Numeric fields
    numeric_fields = ["total_amount", "product_amount", "vat", "discount_amount"]
    for field in numeric_fields:
        if field in data and data[field] is not None:
            try:
                sanitized[field] = float(data[field])
            except (ValueError, TypeError):
                pass

    # Copy other fields as-is
    other_fields = [
        "currency",
        "tran_id",
        "cus_country",
        "ship_country",
        "success_url",
        "fail_url",
        "cancel_url",
        "ipn_url",
    ]

    for field in other_fields:
        if field in data and data[field]:
            sanitized[field] = str(data[field])

    return sanitized


def create_hash_signature(data: Dict[str, Any], secret_key: str) -> str:
    """
    Create hash signature for data verification.

    Args:
        data: Data to create hash for
        secret_key: Secret key for hashing

    Returns:
        Hash signature string
    """
    # Sort keys and create string
    sorted_keys = sorted(data.keys())
    hash_string = ""

    for key in sorted_keys:
        if data[key] is not None:
            hash_string += f"{key}={data[key]}&"

    hash_string = hash_string.rstrip("&")
    hash_string += secret_key

    # Create MD5 hash
    return hashlib.md5(hash_string.encode("utf-8")).hexdigest()


def verify_ipn_hash(ipn_data: Dict[str, Any], secret_key: str) -> bool:
    """
    Verify IPN data hash signature.

    Args:
        ipn_data: IPN data received
        secret_key: Secret key for verification

    Returns:
        True if hash is valid, False otherwise
    """
    received_hash = ipn_data.get("verify_sign", "")
    if not received_hash:
        return True  # No hash to verify

    # Create expected hash
    data_to_hash = ipn_data.copy()
    data_to_hash.pop("verify_sign", None)  # Remove hash from data

    expected_hash = create_hash_signature(data_to_hash, secret_key)

    return received_hash.lower() == expected_hash.lower()


def format_amount_for_display(amount: float, currency: str = "BDT") -> str:
    """
    Format amount for display.

    Args:
        amount: Amount to format
        currency: Currency code

    Returns:
        Formatted amount string
    """
    if currency == "BDT":
        return f"৳ {amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"


def get_currency_symbol(currency: str) -> str:
    """
    Get currency symbol for given currency code.

    Args:
        currency: Currency code

    Returns:
        Currency symbol
    """
    symbols = {
        "BDT": "৳",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CAD": "C$",
        "AUD": "A$",
        "SGD": "S$",
    }

    return symbols.get(currency.upper(), currency)


def is_production_ready() -> bool:
    """
    Check if configuration is ready for production.

    Returns:
        True if ready for production, False otherwise
    """
    config = get_config()

    # Check required settings
    required_settings = ["STORE_ID", "STORE_PASSWORD"]
    for setting in required_settings:
        if not config.get(setting):
            return False

    # Check if not in sandbox mode
    if config.is_sandbox:
        return False

    # Check if URLs are properly configured
    url_settings = ["SUCCESS_URL", "FAIL_URL", "CANCEL_URL", "IPN_URL"]
    for setting in url_settings:
        url = config.get(setting)
        if not url or url.startswith("http://localhost"):
            return False

    return True


def get_environment_info() -> Dict[str, Any]:
    """
    Get environment information for debugging.

    Returns:
        Dictionary containing environment info
    """
    config = get_config()

    return {
        "is_sandbox": config.is_sandbox,
        "store_id": config.store_id[:8] + "..." if config.store_id else None,
        "has_store_password": bool(config.store_password),
        "base_url": config.base_url,
        "production_ready": is_production_ready(),
        "configured_urls": {
            "success": bool(config.get("SUCCESS_URL")),
            "fail": bool(config.get("FAIL_URL")),
            "cancel": bool(config.get("CANCEL_URL")),
            "ipn": bool(config.get("IPN_URL")),
        },
    }
