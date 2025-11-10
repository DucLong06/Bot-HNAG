from django.db import models


class TelegramMessage(models.Model):
    chat_id = models.CharField(max_length=50)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message to {self.chat_id} at {self.sent_at}"
