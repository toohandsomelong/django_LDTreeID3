from django.contrib.auth import views as auth_views
from django.urls import path, include

from accounts import views

name = 'accounts'

urlpatterns = [
    path('', views.index, name='index'),
    path("signup/", views.SignUpView.as_view(), name="signup"),
]