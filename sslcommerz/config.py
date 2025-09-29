"""
Configuration management for SSLCOMMERZ package.
Supports Django settings and environment variables with fallbacks.
"""
import os
from typing import Dict, Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    from decouple import config
except ImportError:
    # Fallback if python-decouple is not available
    def config(key: str, default: Any = None, cast: type = str) -> Any:
        return os.environ.get(key, default)


class SSLCommerzConfig:
    """
    Configuration class for SSLCOMMERZ settings.
    Prioritizes environment variables over Django settings.
    """

    # Default configuration
    DEFAULTS = {
        "IS_SANDBOX": True,
        "TIMEOUT": 30,
        "VERIFY_SSL": True,
        "LOG_REQUESTS": False,
        "AUTO_VALIDATE_IPN": True,
    }

    # Required settings
    REQUIRED = ["STORE_ID", "STORE_PASSWORD"]

    # Optional URL settings
    URL_SETTINGS = ["SUCCESS_URL", "FAIL_URL", "CANCEL_URL", "IPN_URL"]

    def __init__(self):
        self._config = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from environment variables and Django settings."""
        # Start with defaults
        self._config = self.DEFAULTS.copy()

        # Load from Django settings
        django_config = getattr(settings, "SSLCOMMERZ", {})
        self._config.update(django_config)

        # Override with environment variables
        for key in self._get_all_keys():
            env_key = f"SSLCOMMERZ_{key}"
            env_value = config(env_key, default=None)

            if env_value is not None:
                # Cast boolean values
                if key in [
                    "IS_SANDBOX",
                    "VERIFY_SSL",
                    "LOG_REQUESTS",
                    "AUTO_VALIDATE_IPN",
                ]:
                    env_value = config(env_key, default=False, cast=bool)
                elif key == "TIMEOUT":
                    env_value = config(env_key, default=30, cast=int)

                self._config[key] = env_value

    def _get_all_keys(self):
        """Get all possible configuration keys."""
        return (
            self.REQUIRED
            + self.URL_SETTINGS
            + list(self.DEFAULTS.keys())
            + ["STORE_NAME", "CURRENCY"]
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get a configuration value using bracket notation."""
        if key not in self._config:
            raise KeyError(f"Configuration key '{key}' not found")
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        """Check if a configuration key exists."""
        return key in self._config

    @property
    def store_id(self) -> str:
        """Get store ID."""
        return self.get("STORE_ID")

    @property
    def store_password(self) -> str:
        """Get store password."""
        return self.get("STORE_PASSWORD")

    @property
    def is_sandbox(self) -> bool:
        """Check if running in sandbox mode."""
        return self.get("IS_SANDBOX", True)

    @property
    def base_url(self) -> str:
        """Get base API URL based on sandbox mode."""
        if self.is_sandbox:
            return "https://sandbox.sslcommerz.com"
        return "https://securepay.sslcommerz.com"

    @property
    def session_url(self) -> str:
        """Get session initiation URL."""
        return f"{self.base_url}/gwprocess/v4/api.php"

    @property
    def validation_url(self) -> str:
        """Get validation API URL."""
        return f"{self.base_url}/validator/api/validationserverAPI.php"

    @property
    def refund_url(self) -> str:
        """Get refund API URL."""
        return f"{self.base_url}/gwprocess/v4/api.php"

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()


# Global configuration instance
sslcommerz_config = SSLCommerzConfig()


def validate_config() -> None:
    """
    Validate SSLCOMMERZ configuration.
    Raises ImproperlyConfigured if required settings are missing.
    """
    missing_settings = []

    for setting in SSLCommerzConfig.REQUIRED:
        if not sslcommerz_config.get(setting):
            missing_settings.append(setting)

    if missing_settings:
        raise ImproperlyConfigured(
            f"SSLCOMMERZ configuration missing required settings: {', '.join(missing_settings)}. "
            f"Please set them in Django settings.SSLCOMMERZ or as environment variables "
            f"(SSLCOMMERZ_STORE_ID, SSLCOMMERZ_STORE_PASSWORD, etc.)"
        )


def get_config() -> SSLCommerzConfig:
    """Get the global configuration instance."""
    return sslcommerz_config
