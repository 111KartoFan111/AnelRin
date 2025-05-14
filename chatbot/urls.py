from django.urls import path
from . import views

urlpatterns = [
    path('', views.gemini_chat, name='gemini_chat'),
    path('send/', views.gemini_send_message, name='gemini_send_message'),
    path('clear/', views.clear_chat_history, name='clear_chat_history'),
    path('api-key-required/', views.api_key_required, name='api_key_required'), 
    path('about/', views.about_gemini, name='about_gemini'),
]