from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import TelegramService
from members.models import Member
from utils.qr_service import QRService


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_qr_code(request):
    """API để tạo VietQR Quick Link URL (Tập trung logic ở BE)"""
    bank_name = request.data.get('bank_name')
    account_number = request.data.get('account_number')
    amount = request.data.get('amount')
    description = request.data.get('description')
    account_name = request.data.get('account_name')

    if not bank_name or not account_number or not amount:
        return Response({'error': 'bank_name, account_number, and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Gọi hàm tạo URL đã được định nghĩa trong QRService
        qr_url = QRService.get_vietqr_url(
            bank_name=bank_name,
            account_number=account_number,
            amount=amount,
            description=description,
            account_name=account_name
        )

        if qr_url:
            return Response({'qr_url': qr_url})
        else:
            return Response({'error': 'Could not generate QR code. Check bank details.'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"Error in generate_qr_code view: {e}")
        return Response({'error': f'Failed to generate QR: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
