from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})


@require_http_methods(["POST"])
def api_login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return JsonResponse({'message': 'Success', 'user': {
            'username': user.username,
            'is_staff': user.is_staff,
        }})
    return JsonResponse({'error': 'Invalid credentials'}, status=400)


@login_required
def api_user(request):
    return JsonResponse({
        'username': request.user.username,
        'is_staff': request.user.is_staff,
    })


def api_logout(request):
    logout(request)
    return JsonResponse({'message': 'Logged out'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/csrf/', get_csrf_token, name='api-csrf'),
    path('api/login/', api_login, name='api-login'),
    path('api/logout/', api_logout, name='api-logout'),
    path('api/user/', api_user, name='api-user'),
    path('api/members/', include('members.urls')),
    path('api/expenses/', include('expenses.urls')),
    path('api/telegram/', include('telegram_bot.urls')),
]
