from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('email/<int:email_id>/', views.EmailDetailView.as_view(), name='email_detail'),
    path('send_email/', views.SendEmailView.as_view(), name='send_email'),
]
