from django.urls import path
from .views import *
from .views import dashboard, history, logout_view, register

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='dashboard'),
    path('history/<int:client_id>/', history, name='history'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
]
