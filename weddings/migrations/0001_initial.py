# Generated by Django 4.2 on 2025-04-15 20:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название категории')),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Product Categories',
            },
        ),
        migrations.CreateModel(
            name='Wedding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата свадьбы')),
                ('style', models.CharField(choices=[('classic', 'Классическая'), ('modern', 'Современная'), ('rustic', 'Рустик'), ('beach', 'Пляжная'), ('boho', 'Бохо'), ('vintage', 'Винтаж'), ('glamour', 'Гламур'), ('minimalistic', 'Минимализм')], max_length=20, verbose_name='Стиль свадьбы')),
                ('location', models.CharField(blank=True, max_length=255, verbose_name='Место проведения')),
                ('guests_count', models.PositiveIntegerField(default=0, verbose_name='Количество гостей')),
                ('budget', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Бюджет')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название задачи')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('due_date', models.DateField(verbose_name='Срок выполнения')),
                ('completed', models.BooleanField(default=False, verbose_name='Выполнено')),
                ('priority', models.IntegerField(choices=[(1, 'Низкий'), (2, 'Средний'), (3, 'Высокий'), (4, 'Срочный')], default=2, verbose_name='Приоритет')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('wedding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='weddings.wedding')),
            ],
            options={
                'ordering': ['due_date', '-priority'],
            },
        ),
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_date', models.DateTimeField(verbose_name='Дата отправки')),
                ('sent', models.BooleanField(default=False, verbose_name='Отправлено')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='weddings.task')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('image', models.ImageField(upload_to='products/', verbose_name='Изображение')),
                ('style', models.CharField(choices=[('classic', 'Классическая'), ('modern', 'Современная'), ('rustic', 'Рустик'), ('beach', 'Пляжная'), ('boho', 'Бохо'), ('vintage', 'Винтаж'), ('glamour', 'Гламур'), ('minimalistic', 'Минимализм')], max_length=20, verbose_name='Стиль')),
                ('available', models.BooleanField(default=True, verbose_name='В наличии')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='weddings.productcategory')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, verbose_name='Заметки')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weddings.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-added_at'],
                'unique_together': {('user', 'product')},
            },
        ),
    ]
