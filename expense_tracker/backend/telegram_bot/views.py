from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import TelegramService
from members.models import Member


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_debt_reminder(request):
    member_id = request.data.get('member_id')

    if not member_id:
        return Response({'error': 'Member ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        telegram_service = TelegramService()
        success = telegram_service.send_debt_reminder(member_id)

        if success:
            return Response({'message': 'Reminder sent successfully'})
        else:
            return Response({'error': 'Failed to send reminder or no unpaid expenses'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in send_debt_reminder view: {e}")
        return Response({'error': f'Failed to send reminder: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_bulk_reminders(request):
    member_ids = request.data.get('member_ids', [])

    if not member_ids:
        return Response({'error': 'Member IDs are required'}, status=status.HTTP_400_BAD_REQUEST)

    telegram_service = TelegramService()
    results = []

    for member_id in member_ids:
        try:
            success = telegram_service.send_debt_reminder(member_id)
            results.append({'member_id': member_id, 'success': success})
        except Exception as e:
            print(f"Error sending to member {member_id}: {e}")
            results.append({'member_id': member_id, 'success': False, 'error': str(e)})

    successful = sum(1 for r in results if r['success'])
    return Response({
        'message': f'Sent {successful}/{len(results)} reminders successfully',
        'results': results
    })
