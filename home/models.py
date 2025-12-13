from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Email(models.Model):
    id = models.AutoField(primary_key=True)
    sender_email = models.EmailField(max_length=254)
    receiver_email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    send_date = models.DateTimeField(auto_now_add=True)
    is_phishing = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

class UserEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'email')  # Ensure one entry per user-email pair