from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('email/<int:email_id>/', views.EmailDetailView.as_view(), name='email_detail'),
    path('send_email/', views.SendEmailView.as_view(), name='send_email'),
    path('send_email/<str:receiver_email>/', views.SendEmailView.as_view(), name='send_email_to'),
    path('delete_email/<int:email_id>/', views.DeleteEmailView.as_view(), name='delete_email'),
    path('set_unread/<int:email_id>/', views.SetUnreadView.as_view(), name='set_unread'),
    path('set_phishing/<int:email_id>/', views.SetPhishingView.as_view(), name='set_phishing'),
]
