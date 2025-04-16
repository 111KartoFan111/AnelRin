from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Wedding, Task, Product, CartItem, ProductCategory
from .forms import WeddingForm, TaskForm, TaskFilterForm, CartItemForm, ProductFilterForm
from django.utils import timezone
from django.http import JsonResponse


def home(request):
    products = Product.objects.filter(available=True)[:6]
    return render(request, 'weddings/home.html', {'products': products})


@login_required
def wedding_create(request):
    try:
        wedding = Wedding.objects.get(user=request.user)
        return redirect('wedding_edit')
    except Wedding.DoesNotExist:
        pass

    if request.method == 'POST':
        form = WeddingForm(request.POST)
        if form.is_valid():
            wedding = form.save(commit=False)
            wedding.user = request.user
            wedding.save()

            create_default_tasks(wedding)

            messages.success(request, 'Свадьба успешно создана! Теперь вы можете планировать подготовку.')
            return redirect('checklist')
    else:
        form = WeddingForm()

    return render(request, 'weddings/wedding_form.html', {'form': form, 'is_new': True})


@login_required
def wedding_edit(request):
    try:
        wedding = Wedding.objects.get(user=request.user)
    except Wedding.DoesNotExist:
        return redirect('wedding_create')

    if request.method == 'POST':
        form = WeddingForm(request.POST, instance=wedding)
        if form.is_valid():
            form.save()
            messages.success(request, 'Информация о свадьбе успешно обновлена!')
            return redirect('profile')
    else:
        form = WeddingForm(instance=wedding)

    return render(request, 'weddings/wedding_form.html', {'form': form, 'is_new': False})


@login_required
def checklist(request):
    try:
        wedding = Wedding.objects.get(user=request.user)
    except Wedding.DoesNotExist:
        messages.warning(request, 'Сначала создайте свадьбу!')
        return redirect('wedding_create')

    tasks = Task.objects.filter(wedding=wedding)
    filter_form = TaskFilterForm(request.GET)

    if filter_form.is_valid():
        filter_value = filter_form.cleaned_data.get('filter_by')

        if filter_value == 'completed':
            tasks = tasks.filter(completed=True)
        elif filter_value == 'pending':
            tasks = tasks.filter(completed=False)
        elif filter_value == 'overdue':
            tasks = tasks.filter(due_date__lt=timezone.now().date(), completed=False)

    tasks = tasks.order_by('completed', 'due_date')

    context = {
        'tasks': tasks,
        'filter_form': filter_form,
        'wedding': wedding
    }

    return render(request, 'weddings/checklist.html', context)


@login_required
def task_create(request):
    try:
        wedding = Wedding.objects.get(user=request.user)
    except Wedding.DoesNotExist:
        messages.warning(request, 'Сначала создайте свадьбу!')
        return redirect('wedding_create')

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.wedding = wedding
            task.save()
            messages.success(request, 'Задача успешно добавлена!')
            return redirect('checklist')
    else:
        form = TaskForm()

    return render(request, 'weddings/task_form.html', {'form': form})


@login_required
def task_edit(request, pk):

    task = get_object_or_404(Task, pk=pk)

    if task.wedding.user != request.user:
        messages.error(request, 'У вас нет прав для редактирования этой задачи!')
        return redirect('checklist')

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задача успешно обновлена!')
            return redirect('checklist')
    else:
        form = TaskForm(instance=task)

    return render(request, 'weddings/task_form.html', {'form': form, 'task': task})


@login_required
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if task.wedding.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'У вас нет прав для изменения этой задачи!'})

    task.completed = not task.completed
    task.save()

    return JsonResponse({
        'status': 'success',
        'completed': task.completed
    })


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if task.wedding.user != request.user:
        messages.error(request, 'У вас нет прав для удаления этой задачи!')
        return redirect('checklist')

    task.delete()
    messages.success(request, 'Задача успешно удалена!')

    return redirect('checklist')


@login_required
def gallery(request):
    products = Product.objects.filter(available=True)
    categories = ProductCategory.objects.all()

    form = ProductFilterForm(request.GET, categories=categories)

    if form.is_valid():
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        style = form.cleaned_data.get('style')
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
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    in_cart = CartItem.objects.filter(user=request.user, product=product).exists()

    similar_products = Product.objects.filter(
        Q(category=product.category) | Q(style=product.style),
        available=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'in_cart': in_cart,
        'similar_products': similar_products
    }

    return render(request, 'weddings/product_detail.html', context)


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, f'"{product.name}" добавлен в вашу коллекцию!')
    else:
        messages.info(request, f'"{product.name}" уже в вашей коллекции!')

    # 💡 Замена request.is_ajax()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})

    return redirect(request.META.get('HTTP_REFERER', 'gallery'))


@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()

    messages.success(request, f'"{product_name}" удален из вашей коллекции!')

    return redirect('cart')


@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    context = {
        'cart_items': cart_items
    }

    return render(request, 'weddings/cart.html', context)


@login_required
def update_cart_notes(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заметки успешно обновлены!')
            return redirect('cart')
    else:
        form = CartItemForm(instance=cart_item)

    context = {
        'form': form,
        'cart_item': cart_item
    }

    return render(request, 'weddings/cart_item_edit.html', context)


def create_default_tasks(wedding):
    wedding_date = wedding.date

    default_tasks = [
        {'title': 'Определить бюджет свадьбы', 'months_before': 12, 'priority': 4},
        {'title': 'Составить предварительный список гостей', 'months_before': 12, 'priority': 3},
        {'title': 'Выбрать свадебную тему и стиль', 'months_before': 12, 'priority': 3},

        {'title': 'Выбрать и забронировать площадку для церемонии', 'months_before': 9, 'priority': 4},
        {'title': 'Выбрать и забронировать площадку для банкета', 'months_before': 9, 'priority': 4},
        {'title': 'Начать поиск фотографа и видеографа', 'months_before': 9, 'priority': 3},

        {'title': 'Выбрать свадебное платье', 'months_before': 6, 'priority': 4},
        {'title': 'Выбрать костюм жениха', 'months_before': 6, 'priority': 3},
        {'title': 'Забронировать фотографа и видеографа', 'months_before': 6, 'priority': 4},
        {'title': 'Выбрать декоратора и флориста', 'months_before': 6, 'priority': 3},

        {'title': 'Заказать свадебный торт', 'months_before': 4, 'priority': 3},
        {'title': 'Выбрать обручальные кольца', 'months_before': 4, 'priority': 4},
        {'title': 'Отправить приглашения', 'months_before': 4, 'priority': 3},

        {'title': 'Выбрать музыкальное сопровождение', 'months_before': 3, 'priority': 3},
        {'title': 'Организовать транспорт для гостей', 'months_before': 3, 'priority': 2},
        {'title': 'Заказать свадебные аксессуары', 'months_before': 3, 'priority': 2},

        {'title': 'Согласовать меню банкета', 'months_before': 2, 'priority': 3},
        {'title': 'Запланировать репетицию церемонии', 'months_before': 2, 'priority': 2},
        {'title': 'Купить туфли и аксессуары', 'months_before': 2, 'priority': 2},

        {'title': 'Составить план рассадки гостей', 'months_before': 1, 'priority': 3},
        {'title': 'Уточнить список гостей и согласовать с рестораном', 'months_before': 1, 'priority': 4},
        {'title': 'Сделать финальную примерку платья', 'months_before': 1, 'priority': 4},

        {'title': 'Проверить готовность всех организаторов', 'months_before': 0.25, 'priority': 4},
        {'title': 'Подготовить свадебную речь', 'months_before': 0.25, 'priority': 3},
        {'title': 'Подтвердить время со всеми подрядчиками', 'months_before': 0.25, 'priority': 4},
    ]

    for task_info in default_tasks:
        import datetime
        months = task_info['months_before']
        due_date = wedding_date - datetime.timedelta(days=int(months * 30))

        Task.objects.create(
            wedding=wedding,
            title=task_info['title'],
            due_date=due_date,
            priority=task_info['priority']
        )