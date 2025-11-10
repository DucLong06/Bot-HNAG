from rest_framework import serializers
from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'name', 'telegram_id', 'bank_name', 'account_number', 'created_at']  # THÊM bank fields
