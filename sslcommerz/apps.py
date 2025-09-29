"""
Django app configuration for SSLCOMMERZ package.
"""
from django.apps import AppConfig


class SSLCommerzConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sslcommerz"
    verbose_name = "SSLCOMMERZ Payment Gateway"

    def ready(self):
        """
        Perform initialization when Django starts.
        """
        from . import signals  # noqa: F401
        from .config import validate_config

        # Validate configuration on startup
        try:
            validate_config()
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"SSLCOMMERZ configuration warning: {e}")
