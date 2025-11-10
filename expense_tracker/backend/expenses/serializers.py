from rest_framework import serializers
from .models import Expense, ExpenseParticipant
from members.serializers import MemberSerializer


class ExpenseParticipantSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    member_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ExpenseParticipant
        fields = ['id', 'member', 'member_id', 'amount_owed', 'is_paid']


class ExpenseSerializer(serializers.ModelSerializer):
    payer = MemberSerializer(read_only=True)
    payer_id = serializers.IntegerField(write_only=True)
    participants = ExpenseParticipantSerializer(source='expenseparticipant_set', many=True, read_only=True)
    participant_data = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Expense
        fields = ['id', 'name', 'total_amount', 'payer', 'payer_id', 'participants', 'participant_data', 'created_at']

    def create(self, validated_data):
        participant_data = validated_data.pop('participant_data', [])
        expense = Expense.objects.create(**validated_data)

        for participant in participant_data:
            ExpenseParticipant.objects.create(
                expense=expense,
                member_id=participant['member_id'],
                amount_owed=participant['amount_owed']
            )

        return expense

    def update(self, instance, validated_data):
        participant_data = validated_data.pop('participant_data', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if participant_data is not None:
            # Xóa participants cũ và tạo mới
            instance.expenseparticipant_set.all().delete()
            for participant in participant_data:
                ExpenseParticipant.objects.create(
                    expense=instance,
                    member_id=participant['member_id'],
                    amount_owed=participant['amount_owed'],
                    is_paid=participant.get('is_paid', False)
                )

        return instance
