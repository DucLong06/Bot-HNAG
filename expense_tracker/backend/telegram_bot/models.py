from django.db import models
from django.utils import timezone
from members.models import Member
from expenses.models import ExpenseParticipant


class TelegramMessage(models.Model):
    chat_id = models.CharField(max_length=50)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message to {self.chat_id} at {self.sent_at}"


class PaymentConfirmation(models.Model):
    """
    Tracks payment confirmation requests between debtors and lenders.
    Implements two-party verification workflow where either party can initiate
    but counterparty must confirm before marking expenses as paid.
    """

    # Parties involved
    debtor = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='payment_confirmations_as_debtor',
        help_text="Member who owes money"
    )
    lender = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='payment_confirmations_as_lender',
        help_text="Member who receives payment"
    )

    # Payment details
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total amount being confirmed"
    )
    expense_participants = models.ManyToManyField(
        ExpenseParticipant,
        related_name='payment_confirmations',
        help_text="Expense participants being settled"
    )

    # Workflow tracking
    initiated_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='initiated_payment_confirmations',
        help_text="Member who initiated the confirmation request"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('rejected', 'Rejected'),
            ('expired', 'Expired')
        ],
        default='pending',
        help_text="Current status of confirmation request"
    )

    # Telegram integration
    confirmation_message_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Telegram message ID for editing confirmation message"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when confirmation was completed"
    )

    class Meta:
        # Prevent duplicate pending confirmations for same debtor-lender pair
        constraints = [
            models.UniqueConstraint(
                fields=['debtor', 'lender', 'status'],
                condition=models.Q(status='pending'),
                name='unique_pending_confirmation_per_pair'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.debtor.name} → {self.lender.name}: {self.total_amount}đ ({self.status})"

    @property
    def counterparty(self):
        """
        Returns the member who needs to confirm the payment.
        This is the opposite party from whoever initiated the request.
        """
        return self.lender if self.initiated_by == self.debtor else self.debtor


class TelegramUpdateOffset(models.Model):
    """
    Singleton model to store the last processed Telegram update ID.
    Prevents duplicate processing of the same updates when polling.
    """

    offset = models.BigIntegerField(
        default=0,
        help_text="Last processed Telegram update_id"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'telegram_update_offset'

    def __str__(self):
        return f"Last offset: {self.offset} (updated: {self.updated_at})"

    @classmethod
    def get_offset(cls):
        """Get current offset value"""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj.offset

    @classmethod
    def set_offset(cls, new_offset):
        """Update offset to new value"""
        obj, _ = cls.objects.get_or_create(pk=1)
        obj.offset = new_offset
        obj.save()
        return obj
