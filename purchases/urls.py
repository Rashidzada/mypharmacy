from django.urls import path
from . import views

urlpatterns = [
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),
    path('new/', views.purchase_create, name='purchase_create'),
]
