from django.urls import path
from riddles import views

urlpatterns = [
    path('', views.index),
]