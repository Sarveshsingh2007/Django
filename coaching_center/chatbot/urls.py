from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('message/', views.chatbot_message, name='message'),
    path('history/<str:session_id>/', views.chatbot_history, name='history'),
]