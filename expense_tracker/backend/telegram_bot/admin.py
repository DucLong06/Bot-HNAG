from django.contrib import admin
from .models import TelegramMessage, PaymentConfirmation, TelegramUpdateOffset


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'message', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('chat_id', 'message')
    readonly_fields = ('sent_at',)


@admin.register(PaymentConfirmation)
class PaymentConfirmationAdmin(admin.ModelAdmin):
    list_display = ('debtor', 'lender', 'total_amount', 'status', 'initiated_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('debtor__name', 'lender__name')
    readonly_fields = ('created_at', 'confirmed_at', 'confirmation_message_id')
    filter_horizontal = ('expense_participants',)

    fieldsets = (
        ('Parties', {
            'fields': ('debtor', 'lender', 'initiated_by')
        }),
        ('Payment Details', {
            'fields': ('total_amount', 'expense_participants')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'confirmed_at')
        }),
        ('Telegram Integration', {
            'fields': ('confirmation_message_id',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TelegramUpdateOffset)
class TelegramUpdateOffsetAdmin(admin.ModelAdmin):
    list_display = ('offset', 'updated_at')
    readonly_fields = ('offset', 'updated_at')

    def has_add_permission(self, request):
        # Singleton - only one record allowed
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of singleton record
        return False
