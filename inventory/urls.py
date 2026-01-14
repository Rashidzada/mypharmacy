from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/add-stock/', views.add_stock, name='add_stock'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
]
