from django.db import models

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