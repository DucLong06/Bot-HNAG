from django.urls import path
from . import views

urlpatterns = [
    path('send-reminder/', views.send_debt_reminder, name='send_debt_reminder'),
    path('send-bulk-reminders/', views.send_bulk_reminders, name='send_bulk_reminders'),
    path('generate-qr/', views.generate_qr_code, name='generate_qr_code'),  # NEW URL
]
