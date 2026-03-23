"""Public stats endpoint for the dashboard - no auth required."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from expenses.models import Expense, ExpenseParticipant
from members.models import Member

RANKING_LIMIT = 10


@api_view(['GET'])
@permission_classes([AllowAny])
def public_stats(request):
    """Return aggregated fun stats for the public dashboard."""
    expenses = Expense.objects.all()
    participants = ExpenseParticipant.objects.all()

    # --- Overview stats ---
    total_expenses = expenses.count()
    total_spending = expenses.aggregate(total=Sum('total_amount'))['total'] or 0
    total_members = Member.objects.count()
    total_paid = participants.filter(is_paid=True).count()
    total_unpaid = participants.filter(is_paid=False).count()

    # Build avatar URL helper
    def avatar_url(avatar_path):
        if avatar_path and request:
            return request.build_absolute_uri(f'/media/{avatar_path}')
        return None

    # --- Leaderboard rankings (top 10 each) ---

    # Top spenders (payer with highest total amount paid)
    top_spenders = list(
        expenses.values('payer__id', 'payer__name', 'payer__avatar')
        .annotate(total=Sum('total_amount'), count=Count('id'))
        .order_by('-total')[:RANKING_LIMIT]
    )
    for item in top_spenders:
        item['avatar'] = avatar_url(item.pop('payer__avatar'))
        item['name'] = item.pop('payer__name')
        item['total'] = float(item['total'])
        del item['payer__id']

    # Most generous (who treats the most by count)
    most_generous = list(
        expenses.values('payer__id', 'payer__name', 'payer__avatar')
        .annotate(count=Count('id'), total=Sum('total_amount'))
        .order_by('-count')[:RANKING_LIMIT]
    )
    for item in most_generous:
        item['avatar'] = avatar_url(item.pop('payer__avatar'))
        item['name'] = item.pop('payer__name')
        item['total'] = float(item['total'])
        del item['payer__id']

    # Top debtors (most unpaid amount owed, excluding self-debt)
    top_debtors = list(
        participants.filter(is_paid=False)
        .exclude(member=F('expense__payer'))
        .values('member__id', 'member__name', 'member__avatar')
        .annotate(total_owed=Sum('amount_owed'), debt_count=Count('id'))
        .order_by('-total_owed')[:RANKING_LIMIT]
    )
    for item in top_debtors:
        item['avatar'] = avatar_url(item.pop('member__avatar'))
        item['name'] = item.pop('member__name')
        item['total_owed'] = float(item['total_owed'])
        del item['member__id']

    # Longest outstanding debts (oldest unpaid, excluding self-debt)
    longest_debts_qs = (
        participants.filter(is_paid=False)
        .exclude(member=F('expense__payer'))
        .select_related('member', 'expense')
        .order_by('expense__created_at')[:RANKING_LIMIT]
    )
    now = timezone.now()
    longest_debts = []
    for d in longest_debts_qs:
        longest_debts.append({
            'name': d.member.name,
            'avatar': avatar_url(str(d.member.avatar) if d.member.avatar else None),
            'expense_name': d.expense.name,
            'amount': float(d.amount_owed),
            'days_ago': (now - d.expense.created_at).days,
            'date': d.expense.created_at,
        })

    # Biggest meals (most expensive single expenses)
    biggest_meals_qs = (
        expenses.select_related('payer')
        .prefetch_related('expenseparticipant_set')
        .order_by('-total_amount')[:RANKING_LIMIT]
    )
    biggest_meals = []
    for e in biggest_meals_qs:
        biggest_meals.append({
            'name': e.name,
            'amount': float(e.total_amount),
            'payer_name': e.payer.name,
            'payer_avatar': avatar_url(str(e.payer.avatar) if e.payer.avatar else None),
            'participant_count': e.expenseparticipant_set.count(),
            'date': e.created_at,
        })

    # Cleanest members (least total debt among those who have unpaid debt)
    cleanest_members = list(
        participants.filter(is_paid=False)
        .exclude(member=F('expense__payer'))
        .values('member__id', 'member__name', 'member__avatar')
        .annotate(total_owed=Sum('amount_owed'))
        .order_by('total_owed')[:RANKING_LIMIT]
    )
    for item in cleanest_members:
        item['avatar'] = avatar_url(item.pop('member__avatar'))
        item['name'] = item.pop('member__name')
        item['total_owed'] = float(item['total_owed'])
        del item['member__id']

    # --- Charts data ---
    six_months_ago = now - timedelta(days=180)
    monthly_spending = (
        expenses.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_amount'), count=Count('id'))
        .order_by('month')
    )

    spending_by_payer = (
        expenses.values('payer__name', 'payer__avatar')
        .annotate(total=Sum('total_amount'))
        .order_by('-total')[:10]
    )

    return Response({
        'overview': {
            'total_expenses': total_expenses,
            'total_spending': float(total_spending),
            'total_members': total_members,
            'total_paid': total_paid,
            'total_unpaid': total_unpaid,
        },
        'leaderboards': {
            'top_spenders': top_spenders,
            'most_generous': most_generous,
            'top_debtors': top_debtors,
            'longest_debts': longest_debts,
            'biggest_meals': biggest_meals,
            'cleanest_members': cleanest_members,
        },
        'charts': {
            'monthly_spending': [
                {'month': item['month'].strftime('%Y-%m'), 'total': float(item['total']), 'count': item['count']}
                for item in monthly_spending
            ],
            'spending_by_payer': [
                {'name': item['payer__name'], 'total': float(item['total'])}
                for item in spending_by_payer
            ],
        }
    })
