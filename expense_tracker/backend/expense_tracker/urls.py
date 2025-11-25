from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.conf import settings
from django.views.static import serve
import os


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


@require_http_methods(["POST"])
@ensure_csrf_cookie
def api_login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        # Force save session
        request.session.save()
        return JsonResponse({
            'message': 'Success',
            'user': {
                'username': user.username,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            },
            'sessionid': request.session.session_key
        })
    return JsonResponse({'error': 'Invalid credentials'}, status=400)


def api_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
        
    return JsonResponse({
        'username': request.user.username,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
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

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    re_path(r'^(?!api/|admin/|static/|media/).*$',
            TemplateView.as_view(template_name='index.html'),
            name='frontend'),
]
