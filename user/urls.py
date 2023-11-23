"""
URL mappings for the user api
"""
from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManagerUserView.as_view(), name='me'),
]
