from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class GeminiAPIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверка запросов к Gemini API
        if request.path.startswith('/gemini/') and (
           not settings.GEMINI_API_KEY ):
            # Если путь не ведет на страницу с сообщением о необходимости API-ключа
            if not request.path.endswith('/api-key-required/'):
                return redirect(reverse('api_key_required'))
        
        response = self.get_response(request)
        return response