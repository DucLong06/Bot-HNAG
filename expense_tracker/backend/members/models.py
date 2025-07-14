from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=100)
    telegram_id = models.CharField(max_length=50, unique=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)  # THÊM
    account_number = models.CharField(max_length=50, blank=True, null=True)  # THÊM
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
