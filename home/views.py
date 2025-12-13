from django.shortcuts import redirect, render

from home.forms import EmailForm

from .models import Email
from django.views import View

# Create your views here.

class IndexView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        return render(request, 'home/index.html', {'emails': Email.objects.all()})
    
class EmailDetailView(View):
    def get(self, request, email_id):
        if not request.user.is_authenticated:
            return redirect('login')
        email = Email.objects.get(id=email_id)
        return render(request, 'home/email_details.html', {'email': email})
    
class SendEmailView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = EmailForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home:index')
        return redirect('home:index')
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        form = EmailForm()
        return render(request, 'home/send_email.html', {'form': form})
    
class MarkAsReadView(View):
    def post(self, request, email_id):
        if not request.user.is_authenticated:
            return redirect('login')
        email = Email.objects.get(id=email_id)
        email.is_read = True
        email.save()
        return redirect('home:index')
    
class MarkAsPhishingView(View):
    def post(self, request, email_id):
        if not request.user.is_authenticated:
            return redirect('login')
        email = Email.objects.get(id=email_id)
        email.is_phishing = True
        email.save()
        return redirect('home:index')