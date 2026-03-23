"""Public stats endpoint for the dashboard - no auth required."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Sum, Count, Min, Max, F, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from expenses.models import Expense, ExpenseParticipant
from members.models import Member


@api_view(['GET'])
@permission_classes([AllowAny])
def public_stats(request):
    """Return aggregated fun stats for the public dashboard."""
    members = Member.objects.all()
    expenses = Expense.objects.all()
    participants = ExpenseParticipant.objects.all()

    # --- Overview stats ---
    total_expenses = expenses.count()
    total_spending = expenses.aggregate(total=Sum('total_amount'))['total'] or 0
    total_members = members.count()
    total_paid = participants.filter(is_paid=True).count()
    total_unpaid = participants.filter(is_paid=False).count()

    # --- Fun leaderboards ---

    # Top spender (payer with highest total amount paid)
    top_spender = (
        expenses.values('payer__id', 'payer__name', 'payer__avatar')
        .annotate(total=Sum('total_amount'), count=Count('id'))
        .order_by('-total')
        .first()
    )

    # Most frequent payer (who treats the most)
    most_generous = (
        expenses.values('payer__id', 'payer__name', 'payer__avatar')
        .annotate(count=Count('id'), total=Sum('total_amount'))
        .order_by('-count')
        .first()
    )

    # Top debtor (most unpaid amount owed, excluding self-debt)
    top_debtor = (
        participants.filter(is_paid=False)
        .exclude(member=F('expense__payer'))
        .values('member__id', 'member__name', 'member__avatar')
        .annotate(total_owed=Sum('amount_owed'), debt_count=Count('id'))
        .order_by('-total_owed')
        .first()
    )

    # Longest outstanding debt (oldest unpaid expense, excluding self-debt)
    longest_debt = (
        participants.filter(is_paid=False)
        .exclude(member=F('expense__payer'))
        .select_related('member', 'expense')
        .order_by('expense__created_at')
        .first()
    )
    longest_debt_data = None
    if longest_debt:
        days_ago = (timezone.now() - longest_debt.expense.created_at).days
        longest_debt_data = {
            'member_name': longest_debt.member.name,
            'member_avatar': str(longest_debt.member.avatar) if longest_debt.member.avatar else None,
            'expense_name': longest_debt.expense.name,
            'amount': float(longest_debt.amount_owed),
            'days_ago': days_ago,
            'date': longest_debt.expense.created_at,
        }

    # Most expensive single meal
    biggest_meal = expenses.order_by('-total_amount').first()
    biggest_meal_data = None
    if biggest_meal:
        biggest_meal_data = {
            'name': biggest_meal.name,
            'amount': float(biggest_meal.total_amount),
            'payer_name': biggest_meal.payer.name,
            'payer_avatar': str(biggest_meal.payer.avatar) if biggest_meal.payer.avatar else None,
            'participant_count': biggest_meal.expenseparticipant_set.count(),
            'date': biggest_meal.created_at,
        }

    # Cleanest member (least total debt, has participated)
    cleanest_member = (
        participants.filter(is_paid=False)
        .exclude(member=F('expense__payer'))
        .values('member__id', 'member__name', 'member__avatar')
        .annotate(total_owed=Sum('amount_owed'))
        .order_by('total_owed')
        .first()
    )

    # --- Charts data ---

    # Monthly spending trend (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_spending = (
        expenses.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_amount'), count=Count('id'))
        .order_by('month')
    )

    # Spending by payer (for pie chart)
    spending_by_payer = (
        expenses.values('payer__name', 'payer__avatar')
        .annotate(total=Sum('total_amount'))
        .order_by('-total')[:10]
    )

    # Build avatar URL helper
    def build_avatar(avatar_path):
        if avatar_path and request:
            return request.build_absolute_uri(f'/media/{avatar_path}')
        return None

    return Response({
        'overview': {
            'total_expenses': total_expenses,
            'total_spending': float(total_spending),
            'total_members': total_members,
            'total_paid': total_paid,
            'total_unpaid': total_unpaid,
        },
        'leaderboards': {
            'top_spender': {
                'name': top_spender['payer__name'],
                'avatar': build_avatar(top_spender['payer__avatar']),
                'total': float(top_spender['total']),
                'count': top_spender['count'],
            } if top_spender else None,
            'most_generous': {
                'name': most_generous['payer__name'],
                'avatar': build_avatar(most_generous['payer__avatar']),
                'count': most_generous['count'],
                'total': float(most_generous['total']),
            } if most_generous else None,
            'top_debtor': {
                'name': top_debtor['member__name'],
                'avatar': build_avatar(top_debtor['member__avatar']),
                'total_owed': float(top_debtor['total_owed']),
                'debt_count': top_debtor['debt_count'],
            } if top_debtor else None,
            'longest_debt': {
                **longest_debt_data,
                'member_avatar': build_avatar(longest_debt_data['member_avatar']),
            } if longest_debt_data else None,
            'biggest_meal': {
                **biggest_meal_data,
                'payer_avatar': build_avatar(biggest_meal_data['payer_avatar']),
            } if biggest_meal_data else None,
            'cleanest_member': {
                'name': cleanest_member['member__name'],
                'avatar': build_avatar(cleanest_member['member__avatar']),
                'total_owed': float(cleanest_member['total_owed']),
            } if cleanest_member else None,
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
