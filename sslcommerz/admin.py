"""
Django admin configuration for SSLCOMMERZ models.
"""
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Transaction, RefundTransaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model."""

    list_display = [
        "tran_id",
        "customer_name",
        "amount",
        "currency",
        "status",
        "is_validated",
        "created_at",
        "payment_completed_at",
    ]

    list_filter = [
        "status",
        "currency",
        "is_validated",
        "created_at",
        "payment_completed_at",
    ]

    search_fields = [
        "tran_id",
        "val_id",
        "bank_tran_id",
        "customer_name",
        "customer_email",
        "customer_phone",
    ]

    readonly_fields = [
        "tran_id",
        "val_id",
        "bank_tran_id",
        "created_at",
        "updated_at",
        "payment_completed_at",
        "last_validation_at",
        "gateway_response_display",
        "ipn_data_display",
    ]

    fieldsets = (
        (
            "Transaction Information",
            {
                "fields": (
                    "tran_id",
                    "val_id",
                    "bank_tran_id",
                    "status",
                    "amount",
                    "currency",
                    "user",
                )
            },
        ),
        ("Product Information", {"fields": ("product_name", "product_category")}),
        (
            "Customer Information",
            {
                "fields": (
                    "customer_name",
                    "customer_email",
                    "customer_phone",
                    "customer_address",
                )
            },
        ),
        (
            "Validation & Timestamps",
            {
                "fields": (
                    "is_validated",
                    "validation_attempts",
                    "last_validation_at",
                    "created_at",
                    "updated_at",
                    "payment_completed_at",
                )
            },
        ),
        (
            "Gateway Data",
            {
                "fields": ("gateway_response_display", "ipn_data_display"),
                "classes": ("collapse",),
            },
        ),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
    )

    actions = ["validate_selected_transactions", "mark_as_failed"]

    def gateway_response_display(self, obj):
        """Display formatted gateway response."""
        if obj.gateway_response:
            return format_html(
                '<pre style="white-space: pre-wrap; max-height: 200px; overflow-y: auto;">{}</pre>',
                str(obj.gateway_response),
            )
        return "-"

    gateway_response_display.short_description = "Gateway Response"

    def ipn_data_display(self, obj):
        """Display formatted IPN data."""
        if obj.ipn_data:
            return format_html(
                '<pre style="white-space: pre-wrap; max-height: 200px; overflow-y: auto;">{}</pre>',
                str(obj.ipn_data),
            )
        return "-"

    ipn_data_display.short_description = "IPN Data"

    def validate_selected_transactions(self, request, queryset):
        """Admin action to validate selected transactions."""
        from .client import SSLCommerzClient

        client = SSLCommerzClient()
        validated_count = 0

        for transaction in queryset:
            if transaction.val_id:
                try:
                    result = client.validate_transaction(
                        transaction.val_id, str(transaction.amount)
                    )
                    if result.get("status") == "VALID":
                        transaction.is_validated = True
                        transaction.status = "VALIDATED"
                        transaction.last_validation_at = timezone.now()
                        transaction.save()
                        validated_count += 1
                except Exception:
                    pass

        self.message_user(request, f"Validated {validated_count} transactions.")

    validate_selected_transactions.short_description = "Validate selected transactions"

    def mark_as_failed(self, request, queryset):
        """Admin action to mark transactions as failed."""
        updated = queryset.update(status="FAILED")
        self.message_user(request, f"Marked {updated} transactions as failed.")

    mark_as_failed.short_description = "Mark as failed"


@admin.register(RefundTransaction)
class RefundTransactionAdmin(admin.ModelAdmin):
    """Admin interface for RefundTransaction model."""

    list_display = [
        "refund_id",
        "original_transaction",
        "refund_amount",
        "status",
        "created_at",
        "processed_at",
    ]

    list_filter = ["status", "created_at", "processed_at"]

    search_fields = [
        "refund_id",
        "original_transaction__tran_id",
        "original_transaction__customer_name",
    ]

    readonly_fields = [
        "refund_id",
        "created_at",
        "updated_at",
        "processed_at",
        "gateway_response_display",
    ]

    fieldsets = (
        (
            "Refund Information",
            {
                "fields": (
                    "original_transaction",
                    "refund_id",
                    "refund_amount",
                    "refund_reason",
                    "status",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at", "processed_at")}),
        (
            "Gateway Data",
            {"fields": ("gateway_response_display",), "classes": ("collapse",)},
        ),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
    )

    def gateway_response_display(self, obj):
        """Display formatted gateway response."""
        if obj.gateway_response:
            return format_html(
                '<pre style="white-space: pre-wrap; max-height: 200px; overflow-y: auto;">{}</pre>',
                str(obj.gateway_response),
            )
        return "-"

    gateway_response_display.short_description = "Gateway Response"
