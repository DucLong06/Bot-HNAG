from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Expense, ExpenseParticipant
from .serializers import ExpenseSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_paid(self, request, pk=None):
        expense = self.get_object()
        participant_id = request.data.get('participant_id')

        try:
            participant = ExpenseParticipant.objects.get(
                expense=expense,
                member_id=participant_id
            )
            participant.is_paid = not participant.is_paid
            participant.save()
            return Response({'status': 'success'})
        except ExpenseParticipant.DoesNotExist:
            return Response({'error': 'Participant not found'}, status=status.HTTP_404_NOT_FOUND)
