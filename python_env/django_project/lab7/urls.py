from django.urls import path
from . import views

urlpatterns = [
    path('lab7', views.checkPass , name='lab7-checkPass'),
]