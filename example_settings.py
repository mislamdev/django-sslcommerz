"""
Example Django settings configuration for SSLCOMMERZ package.
"""

# Add to your Django settings.py

# Required: Add sslcommerz to INSTALLED_APPS
INSTALLED_APPS = [
    # ... your existing apps
    "sslcommerz",
    # ... other apps
]

# SSLCOMMERZ Configuration
SSLCOMMERZ = {
    # Required settings
    "STORE_ID": "your_store_id_here",  # Get from SSLCOMMERZ merchant panel
    "STORE_PASSWORD": "your_store_password_here",  # Get from SSLCOMMERZ merchant panel
    # Environment settings
    "IS_SANDBOX": True,  # Set to False for production
    # URLs (required for payment flow)
    "SUCCESS_URL": "https://yourdomain.com/payment/success/",
    "FAIL_URL": "https://yourdomain.com/payment/fail/",
    "CANCEL_URL": "https://yourdomain.com/payment/cancel/",
    "IPN_URL": "https://yourdomain.com/payment/ipn/",
    # Optional settings with defaults
    "TIMEOUT": 30,  # API request timeout in seconds
    "VERIFY_SSL": True,  # SSL verification for API requests
    "LOG_REQUESTS": False,  # Log API requests (useful for debugging)
    "AUTO_VALIDATE_IPN": True,  # Automatically validate IPN with SSLCOMMERZ
    # Optional store information
    "STORE_NAME": "Your Store Name",
    "CURRENCY": "BDT",  # Default currency
}

# Logging configuration (optional but recommended)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "sslcommerz.log",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "sslcommerz": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Database configuration (make sure JSONField is supported)
# For Django 3.1+, JSONField is supported in all databases
# For older versions or certain databases, you might need:
# pip install django-jsonfield

# Optional: If using Django REST Framework
if "rest_framework" in INSTALLED_APPS:
    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.BasicAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 20,
    }
