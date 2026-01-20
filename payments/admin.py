from django.contrib import admin
from .models import Payment, Settlement, PaymentHistory

# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payer', 'receiver', 'amount', 'status', 'transaction_ref', 'created_at')
    search_fields = ('payer__full_name', 'receiver__full_name', 'transaction_ref')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('group', 'payer', 'receiver', 'amount', 'payment_mode', 'status', 'created_at', 'paid_requested_at')
    search_fields = ('group__title', 'payer__full_name', 'receiver__full_name')
    list_filter = ('payment_mode', 'status', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'paid_requested_at')


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('settlement', 'paid_by', 'received_by', 'amount', 'payment_mode')
    search_fields = ('paid_by__full_name', 'received_by__full_name', 'settlement__id')
    ordering = ('-settlement__created_at',)