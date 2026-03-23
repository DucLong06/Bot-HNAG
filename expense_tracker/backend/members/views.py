from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from .models import Member, MemberGroup
from .serializers import MemberSerializer, MemberWriteSerializer, MemberAdminSerializer, MemberGroupSerializer
from expenses.models import ExpenseParticipant


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'telegram_id']

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MemberWriteSerializer
        if self.request.user.is_staff:
            return MemberAdminSerializer
        return MemberSerializer

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
            payer = debt.expense.payer
            payer_id = payer.id
            payer_name = payer.name

            # Skip self-debt before accumulating total
            if payer_id == member.id:
                continue

            amount = debt.amount_owed
            total_owed += amount

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


class MemberGroupViewSet(viewsets.ModelViewSet):
    queryset = MemberGroup.objects.prefetch_related('members').all()
    serializer_class = MemberGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by and instance.created_by != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Bạn không có quyền sửa nhóm này (chỉ người tạo mới được sửa)'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by and instance.created_by != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Bạn không có quyền xóa nhóm này'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
