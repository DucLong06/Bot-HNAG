from django.db import models
from members.models import Member


class Expense(models.Model):
    name = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payer = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='paid_expenses')
    participants = models.ManyToManyField(Member, through='ExpenseParticipant')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class ExpenseParticipant(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('expense', 'member')

    def __str__(self):
        return f"{self.member.name} - {self.expense.name}"
