import google.generativeai as genai
from django.conf import settings

def initialize_gemini():
    # Инициализация API-ключа
    genai.configure(api_key=settings.GEMINI_API_KEY)

def get_gemini_model():
    # Получение модели Gemini Pro
    return genai.GenerativeModel('gemini-1.5-pro')

def create_gemini_chat(history=None):
    # Создание чата с историей сообщений
    model = get_gemini_model()
    return model.start_chat(history=history)

def get_wedding_context(wedding):
    """Формирует контекст для чатбота на основе данных о свадьбе"""
    if not wedding:
        return "Пользователь еще не создал свадьбу в системе."
    
    context = f"""
    Информация о свадьбе пользователя:
    - Стиль свадьбы: {wedding.get_style_display()}
    - Дата проведения: {wedding.date.strftime('%d.%m.%Y')}
    - Место проведения: {wedding.location or 'Не указано'}
    - Количество гостей: {wedding.guests_count}
    - Бюджет: {wedding.budget} тенге
    """
    return context