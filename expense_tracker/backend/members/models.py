from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=100)
    telegram_id = models.CharField(max_length=50, unique=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='member_profile'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class MemberGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(Member, related_name='groups', blank=True)
    created_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
