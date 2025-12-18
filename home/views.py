from django.shortcuts import redirect, render
from home.forms import EmailForm
from .models import Email, UserEmail
from django.contrib.auth.models import User
from django.views import View
from visualizeTree.LearningDecisionTree import load_tree, predict, analyze_mail

tree = load_tree()

# Create your views here.

class IndexView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        title = 'Inbox'
        label = request.GET.get('label')
        user_emails = UserEmail.objects.filter(user=request.user, 
                                               is_deleted=False, 
                                               email__receiver_email=request.user.email
                                               ).select_related('email').order_by('-email__send_date')
        match label:
            case None:
                title = 'Inbox'
                user_emails = user_emails.filter(email__is_phishing=False)
            case 'phishing':
                title = 'Phishing'
                user_emails = user_emails.filter(email__is_phishing=True)
            case 'sent':
                title = 'Sent'
                user_emails = UserEmail.objects.filter(user=request.user, 
                                                       is_deleted=False, 
                                                       email__sender_email=request.user.email
                                                       ).select_related('email').order_by('-email__send_date')
        
        unread_count = UserEmail.objects.filter(user=request.user, is_read=False, is_deleted=False, email__is_phishing=False).count()
        phishing_unread_count = UserEmail.objects.filter(user=request.user, is_read=False, is_deleted=False, email__is_phishing=True).count()
        context = {
                    'user_emails': user_emails,
                    'title': title,
                    'unread_count': unread_count,
                    'phishing_unread_count': phishing_unread_count,
                }

        return render(request, 'home/index.html', context)
    
class EmailDetailView(View):
    def get(self, request, email_id):
        if not request.user.is_authenticated:
            return redirect('login')
        email = Email.objects.get(id=email_id)
        UserEmail.objects.filter(user=request.user, email=email).update(is_read=True)
        return render(request, 'home/email_details.html', {'email': email})
    
class SendEmailView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = EmailForm(request.POST)

        if form.is_valid():
            email = form.save(commit=False)
            predicted_label = predict(analyze_mail(form.cleaned_data['body']), tree)[0]
            print(f"Predicted label: {predicted_label}")
            email.is_phishing = predicted_label == '1'
            email.save()

            # Link email to sender and receiver
            UserEmail.objects.create(
                user=request.user,
                email=email,
                is_read=True
            )
            # MultipleObjectsReturned at /send_email/ get() returned more than one UserEmail -- it returned 8!

            UserEmail.objects.create(
                user=User.objects.get(email=form.cleaned_data['receiver_email']),
                email=email
            )
            
            return redirect('home:index')
        return redirect('home:send_email')
    
    def get(self, request, receiver_email=""):
        if not request.user.is_authenticated:
            return redirect('login')
        form = EmailForm()
        return render(request, 'home/send_email.html', {'form': form, 'receiver_email': receiver_email})

class DeleteEmailView(View):
    def post(self, request, email_id):
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_email = UserEmail.objects.get(user=request.user, email__id=email_id)
        user_email.is_deleted = True
        user_email.save()
        return redirect('home:index')
    
class SetUnreadView(View):
    def post(self, request, email_id):
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_email = UserEmail.objects.get(user=request.user, email__id=email_id)
        user_email.is_read = False
        user_email.save()
        return redirect('home:index')
    
class SetPhishingView(View):
    def post(self, request, email_id):
        if not request.user.is_authenticated:
            return redirect('login')
        
        email = Email.objects.get(id=email_id)
        email.is_phishing = True
        email.save()
        return redirect('home:index')