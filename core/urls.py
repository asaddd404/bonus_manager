from django.urls import path
from .views import dashboard, history

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='dashboard'),
    path('history/<int:client_id>/', history, name='history'),
]