from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from weddings.models import Wedding, GeminiChat
from .forms import GeminiChatForm
from .gemini_config import initialize_gemini, create_gemini_chat, get_gemini_model, get_wedding_context
import json

# Инициализация Gemini API
initialize_gemini()

@login_required
def gemini_chat(request):
    # Получаем историю сообщений пользователя
    messages = GeminiChat.objects.filter(user=request.user).order_by('created_at')
    
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == 'AIzaSyDdU9T-qN4rxCbQ_YfJ-XpwhSh70LnG2TU':
        return render(request, 'chatbot/api_key_missing.html')
    # Если истории нет, добавляем приветственное сообщение
    if not messages.exists():
        welcome_message = GeminiChat.objects.create(
            user=request.user,
            message_type='assistant',
            content='Привет! Я ваш свадебный помощник, работающий на базе искусственного интеллекта от Google Gemini. Я могу помочь с идеями и советами для вашей свадьбы. Расскажите, что вас интересует?'
        )
        messages = [welcome_message]
    
    form = GeminiChatForm()
    
    # Проверяем, есть ли свадьба у пользователя
    try:
        wedding = Wedding.objects.get(user=request.user)
        has_wedding = True
    except Wedding.DoesNotExist:
        has_wedding = False
        wedding = None
    
    context = {
        'messages': messages,
        'form': form,
        'has_wedding': has_wedding,
        'wedding': wedding
    }
    
    return render(request, 'chatbot/gemini_chat.html', context)

@login_required
def gemini_send_message(request):
    if request.method == 'POST':
        form = GeminiChatForm(request.POST)
        if form.is_valid():
            # Сохраняем сообщение пользователя
            user_message = form.save(commit=False)
            user_message.user = request.user
            user_message.message_type = 'user'
            user_message.save()
            
            try:
                # Получаем свадьбу пользователя
                try:
                    wedding = Wedding.objects.get(user=request.user)
                    wedding_context = get_wedding_context(wedding)
                except Wedding.DoesNotExist:
                    wedding = None
                    wedding_context = "Пользователь еще не создал свадьбу в системе."
                
                # Формируем историю для модели
                history = []
                system_prompt = f"""
                Ты - свадебный помощник для приложения Wedding Planner. Твоя задача - помогать с планированием свадьбы,
                давать советы и идеи по организации. Используй данные о свадьбе пользователя, чтобы давать персонализированные рекомендации.
                Будь дружелюбным, полезным и конкретным. Предлагай креативные идеи для различных аспектов свадьбы, учитывая стиль, бюджет и другие параметры.
                
                {wedding_context}
                
                Если пользователь еще не создал свадьбу, мягко предложи ему сделать это для более персонализированных рекомендаций.
                
                Отвечай на русском языке, даже если пользователь пишет на другом языке.
                """
                
                # Добавляем системный промпт в начало истории
                history.append({"role": "system", "parts": [system_prompt]})
                
                # Добавляем историю сообщений (последние 10 сообщений)
                previous_messages = GeminiChat.objects.filter(user=request.user).order_by('-created_at')[:10][::-1]
                for msg in previous_messages:
                    role = "user" if msg.message_type == "user" else "model"
                    history.append({"role": role, "parts": [msg.content]})
                
                # Получаем модель и отправляем запрос
                model = get_gemini_model()
                response = model.generate_content(
                    history + [{"role": "user", "parts": [user_message.content]}]
                )
                
                # Сохраняем ответ от Gemini
                bot_response = response.text
                bot_message = GeminiChat.objects.create(
                    user=request.user,
                    message_type='assistant',
                    content=bot_response
                )
                
                return JsonResponse({
                    'status': 'success',
                    'user_message': {
                        'content': user_message.content,
                        'created_at': user_message.created_at.strftime('%H:%M')
                    },
                    'bot_message': {
                        'content': bot_message.content,
                        'created_at': bot_message.created_at.strftime('%H:%M')
                    }
                })
                
            except Exception as e:
                print(f"Error: {str(e)}")
                # В случае ошибки с Gemini API, используем резервный ответ
                fallback_response = "Извините, в данный момент я не могу обработать ваш запрос. Пожалуйста, попробуйте позже."
                bot_message = GeminiChat.objects.create(
                    user=request.user,
                    message_type='assistant',
                    content=fallback_response
                )
                
                return JsonResponse({
                    'status': 'error',
                    'user_message': {
                        'content': user_message.content,
                        'created_at': user_message.created_at.strftime('%H:%M')
                    },
                    'bot_message': {
                        'content': bot_message.content,
                        'created_at': bot_message.created_at.strftime('%H:%M')
                    }
                })
    
    return JsonResponse({'status': 'error'})

@login_required
def clear_chat_history(request):
    if request.method == 'POST':
        # Удаляем всю историю чата пользователя
        GeminiChat.objects.filter(user=request.user).delete()
        
        # Создаем новое приветственное сообщение
        welcome_message = GeminiChat.objects.create(
            user=request.user,
            message_type='assistant',
            content='Я очистил историю нашего разговора. Чем я могу помочь вам сегодня с планированием свадьбы?'
        )
        
        return JsonResponse({
            'status': 'success',
            'bot_message': {
                'content': welcome_message.content,
                'created_at': welcome_message.created_at.strftime('%H:%M')
            }
        })
    
    return JsonResponse({'status': 'error'})

def api_key_required(request):
    return render(request, 'chatbot/api_key_missing.html')


def about_gemini(request):
    return render(request, 'chatbot/about_gemini.html')