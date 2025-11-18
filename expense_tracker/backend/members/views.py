from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from .models import Member
from .serializers import MemberSerializer
from expenses.models import ExpenseParticipant


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'telegram_id']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def debt_summary(self, request, pk=None):
        member = self.get_object()

        unpaid_debts = ExpenseParticipant.objects.filter(
            member=member,
            is_paid=False
        ).select_related('expense', 'expense__payer').order_by('expense__created_at')

        total_owed = 0
        details_by_payer = {}

        for debt in unpaid_debts:
            amount = debt.amount_owed
            total_owed += amount

            payer = debt.expense.payer
            payer_id = payer.id
            payer_name = payer.name

            if payer_id == member.id:
                continue

            if payer_id not in details_by_payer:
                details_by_payer[payer_id] = {
                    'payer_id': payer_id,
                    'payer_name': payer_name,
                    'bank_name': payer.bank_name,
                    'account_number': payer.account_number,
                    'total_owed_to_payer': 0,
                    'expenses': []
                }

            details_by_payer[payer_id]['total_owed_to_payer'] += amount
            details_by_payer[payer_id]['expenses'].append({
                'expense_id': debt.expense.id,
                'expense_name': debt.expense.name,
                'amount': amount,
                'date': debt.expense.created_at,
                'participant_id': debt.id
            })

        return Response({
            'member_id': member.id,
            'member_name': member.name,
            'total_owed': total_owed,
            'debt_count': unpaid_debts.count(),
            'details': list(details_by_payer.values())
        })
