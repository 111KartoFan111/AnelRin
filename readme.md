
## Настройка проекта

1. Клонировать репозиторий:
   ```bash
    git clone [https://github.com//wedding-planner.git](https://github.com/your-repo/wedding-planner.git)
    ```

2. Создайте виртуальное окружение Python :
    ```bash
    source venv/bin/activate
    ```

3. Установите зависимости из файла requirements.txt
    ```bash
    pip install -r requirements.txt
    ```

4. Перейдите в папку проекта:
    ```bash
    cd wedding-planner
    ```

5. Cоздайте суперпользователя :
    ```bash
    python manage.py createsuperuser
    ```

## Запуск проекта

Запустите сервер разработки:
   ```bash
    python manage.py runserver
    ```

## Обьяснение кода

## 1. Настройка проекта (wedding_planner)

### settings.py
Основной файл настроек Django:
```python
# Настройки базы данных - используется SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Установленные приложения
INSTALLED_APPS = [
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    # ...

    # Пользовательские приложения
    'users.apps.UsersConfig',
    'weddings.apps.WeddingsConfig',

    # Сторонние библиотеки
    'crispy_forms',
    'crispy_bootstrap5',
]

# Настройки для crispy forms (красивые формы)
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Настройки авторизации
LOGIN_REDIRECT_URL = 'home'  # Куда перенаправлять после входа
LOGIN_URL = 'login'  # Страница входа
```

### urls.py
Распределяет запросы между приложениями:
```python
urlpatterns = [
    path('admin/', admin.site.urls),  # Админ-панель Django
    path('', include('weddings.urls')),  # Основные URL (главная, свадьба, галерея)
    path('users/', include('users.urls')),  # URL авторизации и профиля
]
```

## 2. Приложение Users

### models.py
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    
    # Связь один-к-одному с пользователем Django
    # При удалении пользователя профиль тоже удаляется (CASCADE)
```

### signals.py
```python
# Автоматически создает профиль при создании пользователя
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Автоматически сохраняет профиль при сохранении пользователя
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
```

### views.py
```python
def register(request):
    # Обработка формы регистрации
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняет пользователя
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required  # Доступно только авторизованным
def profile(request):
    # Редактирование профиля
    if request.method == 'POST':
        # Обновление данных пользователя и профиля
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('profile')
    else:
        # Загрузка текущих данных в формы
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Проверка наличия свадьбы у пользователя
    try:
        wedding = Wedding.objects.get(user=request.user)
        has_wedding = True
    except Wedding.DoesNotExist:
        has_wedding = False
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'has_wedding': has_wedding
    }
    return render(request, 'users/profile.html', context)
```

## 3. Приложение Weddings - Модели

### models.py
```python
class Wedding(models.Model):
    # Варианты стилей свадьбы
    STYLE_CHOICES = [
        ('classic', 'Классическая'),
        ('modern', 'Современная'),
        ('rustic', 'Рустик'),
        # ...
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Один пользователь - одна свадьба
    date = models.DateField(verbose_name='Дата свадьбы')
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, verbose_name='Стиль свадьбы')
    location = models.CharField(max_length=255, blank=True, verbose_name='Место проведения')
    guests_count = models.PositiveIntegerField(default=0, verbose_name='Количество гостей')
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Бюджет')

class Task(models.Model):
    # Уровни приоритета задачи
    PRIORITY_CHOICES = [
        (1, 'Низкий'),
        (2, 'Средний'),
        (3, 'Высокий'),
        (4, 'Срочный'),
    ]
    
    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255, verbose_name='Название задачи')
    description = models.TextField(blank=True, verbose_name='Описание')
    due_date = models.DateField(verbose_name='Срок выполнения')
    completed = models.BooleanField(default=False, verbose_name='Выполнено')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name='Приоритет')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['due_date', '-priority']  # Сортировка: сначала по дате, потом по приоритету
    
    def is_overdue(self):
        # Проверяет, просрочена ли задача
        return self.due_date < timezone.now().date() and not self.completed

class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    image = models.ImageField(upload_to='products/', verbose_name='Изображение')
    style = models.CharField(max_length=20, choices=Wedding.STYLE_CHOICES, verbose_name='Стиль')
    available = models.BooleanField(default=True, verbose_name='В наличии')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, verbose_name='Заметки')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')  # Товар может быть только один раз в коллекции
```

## 4. Приложение Weddings - Ключевые представления

### views.py - Управление свадьбой

```python
@login_required
def wedding_create(request):
    # Проверка, есть ли уже свадьба у пользователя
    try:
        wedding = Wedding.objects.get(user=request.user)
        return redirect('wedding_edit')  # Если есть - редактировать существующую
    except Wedding.DoesNotExist:
        pass  # Если нет - создать новую
    
    if request.method == 'POST':
        form = WeddingForm(request.POST)
        if form.is_valid():
            wedding = form.save(commit=False)  # Не сохранять сразу
            wedding.user = request.user  # Привязать к текущему пользователю
            wedding.save()
            
            # Создать стандартный набор задач
            create_default_tasks(wedding)
            
            messages.success(request, 'Свадьба создана!')
            return redirect('checklist')
    else:
        form = WeddingForm()
    
    return render(request, 'weddings/wedding_form.html', {'form': form, 'is_new': True})
```

### views.py - Чек-лист задач

```python
@login_required
def checklist(request):
    # Проверка наличия свадьбы
    try:
        wedding = Wedding.objects.get(user=request.user)
    except Wedding.DoesNotExist:
        messages.warning(request, 'Сначала создайте свадьбу!')
        return redirect('wedding_create')
    
    # Получение и фильтрация задач
    tasks = Task.objects.filter(wedding=wedding)
    filter_form = TaskFilterForm(request.GET)
    
    if filter_form.is_valid():
        filter_value = filter_form.cleaned_data.get('filter_by')
        
        # Применение фильтров
        if filter_value == 'completed':
            tasks = tasks.filter(completed=True)
        elif filter_value == 'pending':
            tasks = tasks.filter(completed=False)
        elif filter_value == 'overdue':
            tasks = tasks.filter(due_date__lt=timezone.now().date(), completed=False)
    
    tasks = tasks.order_by('completed', 'due_date')  # Сортировка задач
    
    context = {
        'tasks': tasks,
        'filter_form': filter_form,
        'wedding': wedding
    }
    
    return render(request, 'weddings/checklist.html', context)

@login_required
def task_toggle(request, pk):
    # Переключение статуса задачи (AJAX-запрос)
    task = get_object_or_404(Task, pk=pk)
    
    # Проверка прав доступа
    if task.wedding.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'Нет прав!'})
    
    # Переключение статуса
    task.completed = not task.completed
    task.save()
    
    # Отправка результата в JSON для обновления интерфейса
    return JsonResponse({
        'status': 'success',
        'completed': task.completed
    })
```

### views.py - Галерея и коллекция

```python
@login_required
def gallery(request):
    # Получение всех доступных товаров
    products = Product.objects.filter(available=True)
    categories = ProductCategory.objects.all()
    
    # Обработка фильтров
    form = ProductFilterForm(request.GET, categories=categories)
    
    if form.is_valid():
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        style = form.cleaned_data.get('style')
        
        # Применение фильтров
        if category:
            products = products.filter(category_id=category)
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        if style:
            products = products.filter(style=style)
    
    context = {
        'products': products,
        'form': form
    }
    
    return render(request, 'weddings/gallery.html', context)

@login_required
def add_to_cart(request, pk):
    # Добавление товара в коллекцию
    product = get_object_or_404(Product, pk=pk)
    
    # Создание записи в коллекции (если нет) или возврат существующей
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    
    # Разные сообщения в зависимости от результата
    if created:
        messages.success(request, f'"{product.name}" добавлен в коллекцию!')
    else:
        messages.info(request, f'"{product.name}" уже в коллекции!')
    
    # Поддержка AJAX-запросов
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # Возврат на предыдущую страницу
    return redirect(request.META.get('HTTP_REFERER', 'gallery'))
```

## 5. Автоматическое создание задач

```python
def create_default_tasks(wedding):
    wedding_date = wedding.date
    
    # Шаблон задач: название, за сколько месяцев, приоритет
    default_tasks = [
        {'title': 'Определить бюджет свадьбы', 'months_before': 12, 'priority': 4},
        {'title': 'Составить список гостей', 'months_before': 12, 'priority': 3},
        # ...и так далее
    ]
    
    # Создание задач для свадьбы
    for task_info in default_tasks:
        months = task_info['months_before']
        # Расчет даты задачи относительно даты свадьбы
        due_date = wedding_date - datetime.timedelta(days=int(months * 30))
        
        # Создание задачи
        Task.objects.create(
            wedding=wedding,
            title=task_info['title'],
            due_date=due_date,
            priority=task_info['priority']
        )
```

## 6. Система напоминаний

```python
# weddings/management/commands/send_reminders.py
class Command(BaseCommand):
    help = 'Отправляет напоминания о предстоящих задачах'
    
    def handle(self, *args, **options):
        # Текущая дата
        today = timezone.now().date()
        
        # Напоминания о предстоящих задачах
        self.send_upcoming_task_reminders(today)
        
        # Напоминания о просроченных задачах
        self.send_overdue_task_reminders(today)
        
        # Генерация будущих напоминаний
        self.generate_future_reminders()
    
    def send_upcoming_task_reminders(self, today):
        # Напоминания за 1, 3, 7, 14 дней до срока
        reminder_days = [1, 3, 7, 14]
        
        for days in reminder_days:
            # Вычисление даты для напоминания
            reminder_date = today + datetime.timedelta(days=days)
            
            # Поиск задач с этой датой выполнения
            tasks = Task.objects.filter(due_date=reminder_date, completed=False)
            
            # Отправка напоминаний
            for task in tasks:
                # Проверка, не отправлялось ли уже сегодня
                reminder_exists = Reminder.objects.filter(
                    task=task, send_date__date=today, sent=True
                ).exists()
                
                if not reminder_exists:
                    # Отправка email с напоминанием
                    self.send_reminder_email(task, days, False)
                    
                    # Создание записи об отправке
                    Reminder.objects.create(
                        task=task, send_date=timezone.now(), sent=True
                    )
```

## 7. JavaScript для интерактивности (пример из шаблона checklist.html)

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Находим все чекбоксы задач
    const taskToggleCheckboxes = document.querySelectorAll('.task-toggle');
    
    // Для каждого чекбокса добавляем обработчик
    taskToggleCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskId = this.getAttribute('data-task-id');
            const completed = this.checked;
            
            // AJAX-запрос для обновления статуса задачи
            fetch(`/task/${taskId}/toggle/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Обновление внешнего вида карточки задачи
                    const taskCard = this.closest('.task-card');
                    if (data.completed) {
                        taskCard.classList.add('task-completed');
                    } else {
                        taskCard.classList.remove('task-completed');
                    }
                } else {
                    // Обработка ошибки
                    alert('Произошла ошибка. Попробуйте еще раз.');
                    this.checked = !this.checked;
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка. Попробуйте еще раз.');
                this.checked = !this.checked;
            });
        });
    });
    
    // Получение значения cookie для CSRF-токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
```

## 8. Взаимодействие компонентов системы

1. **Регистрация пользователя**:
   - Пользователь отправляет форму регистрации
   - Django создает пользователя
   - Сигналы Django автоматически создают профиль
   - Пользователь перенаправляется на страницу входа

2. **Создание свадьбы**:
   - Пользователь заполняет форму свадьбы
   - Django создает запись в модели Wedding
   - Функция `create_default_tasks` автоматически создает задачи
   - Пользователь перенаправляется в чек-лист

3. **Работа с чек-листом**:
   - Пользователь отмечает задачу как выполненную
   - JavaScript отправляет AJAX-запрос
   - Django обновляет запись в базе данных
   - JavaScript обновляет внешний вид задачи без перезагрузки страницы

4. **Система напоминаний**:
   - Команда `send_reminders` запускается по расписанию
   - Для каждой предстоящей задачи создается напоминание
   - Напоминание отправляется по электронной почте

5. **Галерея идей**:
   - Пользователь применяет фильтры
   - Django фильтрует товары по категории, цене и стилю
   - Пользователь добавляет товар в коллекцию
   - Django создает запись в модели CartItem

## 9. Безопасность и валидация

- **Декоратор `@login_required`** - защищает маршруты от неавторизованных пользователей
- **Проверки владельца** - например, проверка, что пользователь редактирует только свои задачи:
  ```python
  if task.wedding.user != request.user:
      return JsonResponse({'status': 'error', 'message': 'Нет прав!'})
  ```

## 10. Шаблоны Django

Шаблоны используют наследование для повторного использования кода:

```html
<!-- base.html - базовый шаблон -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Wedding Planner{% endblock %}</title>
    <!-- ... -->
</head>
<body>
    {% include 'includes/navbar.html' %}
    
    <main class="container py-4">
        {% if messages %}
            <!-- Вывод системных сообщений -->
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>
    
    {% include 'includes/footer.html' %}
</body>
</html>

<!-- checklist.html - наследует от базового -->
{% extends "base.html" %}

{% block title %}Чек-лист | Wedding Planner{% endblock %}

{% block content %}
    <!-- Содержимое страницы чек-листа -->
{% endblock %}
```