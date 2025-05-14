from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Wedding(models.Model):
    STYLE_CHOICES = [
        ('classic', 'Классическая'),
        ('modern', 'Современная'),
        ('rustic', 'Рустик'),
        ('beach', 'Пляжная'),
        ('boho', 'Бохо'),
        ('vintage', 'Винтаж'),
        ('glamour', 'Гламур'),
        ('minimalistic', 'Минимализм'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Дата свадьбы')
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, verbose_name='Стиль свадьбы')
    location = models.CharField(max_length=255, blank=True, verbose_name='Место проведения')
    guests_count = models.PositiveIntegerField(default=0, verbose_name='Количество гостей')
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Бюджет')

    def __str__(self):
        return f'Свадьба {self.user.username} - {self.date}'


class Task(models.Model):
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
        ordering = ['due_date', '-priority']

    def __str__(self):
        return self.title
    def is_overdue(self):
        return self.due_date < timezone.now().date() and not self.completed


class Reminder(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='reminders')
    send_date = models.DateTimeField(verbose_name='Дата отправки')
    sent = models.BooleanField(default=False, verbose_name='Отправлено')
    def __str__(self):
        return f'Напоминание о {self.task.title} - {self.send_date}'


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(unique=True)
    class Meta:
        verbose_name_plural = 'Product Categories'

    def __str__(self):
        return self.name


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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id])


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, verbose_name='Заметки')
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'
    
class GeminiChat(models.Model):
    MESSAGE_TYPES = [
        ('user', 'Пользователь'),
        ('assistant', 'Ассистент'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gemini_chats')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}"