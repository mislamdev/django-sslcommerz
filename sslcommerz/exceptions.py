"""
Custom exceptions for SSLCOMMERZ package.
"""


class SSLCommerzError(Exception):
    """Base exception for all SSLCOMMERZ related errors."""

    pass


class SSLCommerzConfigError(SSLCommerzError):
    """Raised when there's a configuration error."""

    pass


class SSLCommerzAPIError(SSLCommerzError):
    """Raised when SSLCOMMERZ API returns an error."""

    pass


class SSLCommerzValidationError(SSLCommerzError):
    """Raised when data validation fails."""

    pass


class SSLCommerzIPNError(SSLCommerzError):
    """Raised when IPN processing fails."""

    pass
