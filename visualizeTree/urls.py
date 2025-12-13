from django.urls import path, include

from visualizeTree import views

name = 'visualizeTree'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]