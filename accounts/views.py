from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from accounts.forms import SignUpForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from home.models import Email

@login_required
def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'registration/index.html')

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

@login_required
def update_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            request.user.email = email
            request.user.save()
            messages.success(request, 'Email updated successfully.')
            Email.objects.filter(receiver_email=request.user.email).update(receiver_email=email)
        else:
            messages.error(request, 'Email is required.')
    return redirect('accounts:index')