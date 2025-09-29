"""
Django models for SSLCOMMERZ transaction tracking.
"""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Transaction(models.Model):
    """
    Model to track SSLCOMMERZ transactions.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("VALID", "Valid"),
        ("VALIDATED", "Validated"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
        ("REFUNDED", "Refunded"),
        ("PARTIALLY_REFUNDED", "Partially Refunded"),
    ]

    # Transaction identifiers
    tran_id = models.CharField(max_length=100, unique=True, db_index=True)
    val_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    bank_tran_id = models.CharField(max_length=100, blank=True, null=True)

    # User relationship (optional)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sslcommerz_transactions",
    )

    # Transaction details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="BDT")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    # Product information
    product_name = models.CharField(max_length=255, blank=True)
    product_category = models.CharField(max_length=100, blank=True)

    # Customer information
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField(blank=True)

    # Gateway response data
    gateway_response = models.JSONField(default=dict, blank=True)
    ipn_data = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_completed_at = models.DateTimeField(null=True, blank=True)

    # Validation
    is_validated = models.BooleanField(default=False)
    validation_attempts = models.PositiveIntegerField(default=0)
    last_validation_at = models.DateTimeField(null=True, blank=True)

    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "SSLCOMMERZ Transaction"
        verbose_name_plural = "SSLCOMMERZ Transactions"
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["customer_email", "created_at"]),
        ]

    def __str__(self):
        return f"{self.tran_id} - {self.amount} {self.currency} ({self.status})"

    def mark_as_successful(self):
        """Mark transaction as successful."""
        self.status = "VALID"
        self.payment_completed_at = timezone.now()
        self.save(update_fields=["status", "payment_completed_at", "updated_at"])

    def mark_as_failed(self, reason=None):
        """Mark transaction as failed."""
        self.status = "FAILED"
        if reason:
            self.metadata["failure_reason"] = reason
        self.save(update_fields=["status", "metadata", "updated_at"])

    def update_from_ipn(self, ipn_data):
        """Update transaction from IPN data."""
        self.ipn_data = ipn_data
        self.val_id = ipn_data.get("val_id", self.val_id)
        self.bank_tran_id = ipn_data.get("bank_tran_id", self.bank_tran_id)

        # Update status if provided
        new_status = ipn_data.get("status")
        if new_status and new_status.upper() in dict(self.STATUS_CHOICES):
            self.status = new_status.upper()

        self.save()

    @property
    def is_successful(self):
        """Check if transaction is successful."""
        return self.status in ["VALID", "VALIDATED"]

    @property
    def is_pending(self):
        """Check if transaction is pending."""
        return self.status == "PENDING"

    @property
    def can_be_refunded(self):
        """Check if transaction can be refunded."""
        return self.is_successful and self.status != "REFUNDED"


class RefundTransaction(models.Model):
    """
    Model to track refund transactions.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    # Related transaction
    original_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="refunds"
    )

    # Refund details
    refund_id = models.CharField(max_length=100, unique=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    # Gateway response
    gateway_response = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "SSLCOMMERZ Refund"
        verbose_name_plural = "SSLCOMMERZ Refunds"

    def __str__(self):
        return f"Refund {self.refund_id} - {self.refund_amount} ({self.status})"
