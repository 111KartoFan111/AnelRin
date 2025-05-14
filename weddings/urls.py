from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('wedding/create/', views.wedding_create, name='wedding_create'),
    path('wedding/edit/', views.wedding_edit, name='wedding_edit'),

    path('checklist/', views.checklist, name='checklist'),
    path('task/create/', views.task_create, name='task_create'),
    path('task/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:pk>/toggle/', views.task_toggle, name='task_toggle'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),

    path('gallery/', views.gallery, name='gallery'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart, name='cart'),
    path('product/<int:pk>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart-item/<int:pk>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart-item/<int:pk>/update/', views.update_cart_notes, name='update_cart_notes'),
]