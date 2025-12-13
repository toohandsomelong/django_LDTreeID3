from django import forms
from .models import Email

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['sender_email', 'receiver_email', 'subject', 'body', 'is_phishing']