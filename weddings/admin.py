from django.contrib import admin
from .models import Wedding, Task, Reminder, ProductCategory, Product, CartItem


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'style', 'location', 'guests_count', 'budget')
    list_filter = ('style', 'date')
    search_fields = ('user__username', 'location')
    date_hierarchy = 'date'


class ReminderInline(admin.TabularInline):
    model = Reminder
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'wedding', 'due_date', 'priority', 'completed')
    list_filter = ('completed', 'priority', 'due_date')
    search_fields = ('title', 'description', 'wedding__user__username')
    date_hierarchy = 'due_date'
    inlines = [ReminderInline]


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('task', 'send_date', 'sent')
    list_filter = ('sent', 'send_date')
    search_fields = ('task__title',)
    date_hierarchy = 'send_date'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'style', 'available')
    list_filter = ('available', 'category', 'style')
    search_fields = ('name', 'description')
    list_editable = ('price', 'available')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name', 'notes')