from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Expense, ExpenseParticipant
from .serializers import ExpenseSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related('payer', 'created_by').prefetch_related(
        'expenseparticipant_set__member').all()
    serializer_class = ExpenseSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payer']
    search_fields = ['name', 'payer__name']
    ordering_fields = ['created_at', 'total_amount']

    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    # ---------------------------------------------

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by and instance.created_by != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Bạn không có quyền sửa khoản chi này (chỉ người tạo mới được sửa)'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by and instance.created_by != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Bạn không có quyền xóa khoản chi này'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_paid(self, request, pk=None):
        expense = self.get_object()

        if expense.created_by and expense.created_by != request.user and not request.user.is_superuser:
            return Response(
                {'error': 'Chỉ người tạo đơn mới có quyền xác nhận thanh toán'},
                status=status.HTTP_403_FORBIDDEN
            )

        participant_id = request.data.get('participant_id')

        try:
            participant = ExpenseParticipant.objects.get(
                expense=expense,
                member_id=participant_id
            )
            participant.is_paid = not participant.is_paid
            participant.save()
            return Response({'status': 'success', 'is_paid': participant.is_paid})
        except ExpenseParticipant.DoesNotExist:
            return Response({'error': 'Participant not found'}, status=status.HTTP_404_NOT_FOUND)
